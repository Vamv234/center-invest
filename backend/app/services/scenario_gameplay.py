from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.attempt_events import attempt_event_broker
from app.models.scenario_gameplay import (
    TrainingAttempt,
    TrainingAttemptAnswer,
    TrainingEventLog,
    TrainingScenario,
    TrainingScenarioStep,
    TrainingStepOption,
)
from app.models.user import User
from app.schemas.progress import AttemptErrorInput, ScenarioAttemptCreate
from app.schemas.scenario_gameplay import (
    AnswerFeedbackOut,
    AttemptAnswerResultOut,
    AttemptEventOut,
    AttemptStateOut,
    HintResultOut,
    ScenarioCard,
    ScenarioMeta,
    StepOptionOut,
    StepOut,
)
from app.services.progress import progress_service


class ScenarioGameplayService:
    HINT_PENALTY = 2

    async def seed_scenarios(self, db: AsyncSession, *, seed_path: str) -> None:
        total = await db.scalar(select(func.count(TrainingScenario.id)))
        if int(total or 0) > 0:
            return

        raw = json.loads(Path(seed_path).read_text(encoding="utf-8"))
        for scenario_payload in raw.get("scenarios", []):
            scenario = TrainingScenario(
                id=scenario_payload["id"],
                title=scenario_payload["title"],
                level=scenario_payload["level"],
                setting=scenario_payload["setting"],
                summary=scenario_payload["summary"],
                threat_types=list(scenario_payload.get("threat_types", [])),
                start_step_id=scenario_payload["start_step_id"],
                passing_score=int(scenario_payload.get("passing_score", 0)),
            )
            db.add(scenario)

            for step_index, step_payload in enumerate(scenario_payload.get("steps", [])):
                step = TrainingScenarioStep(
                    id=step_payload["id"],
                    scenario_id=scenario.id,
                    order_index=step_index,
                    title=step_payload["title"],
                    prompt=step_payload["prompt"],
                    hint=step_payload["hint"],
                    explanation=step_payload["explanation"],
                )
                db.add(step)

                for option_index, option_payload in enumerate(step_payload.get("options", [])):
                    db.add(
                        TrainingStepOption(
                            id=option_payload["id"],
                            step_id=step.id,
                            order_index=option_index,
                            label=option_payload["label"],
                            outcome=option_payload.get("outcome"),
                            is_safe=bool(option_payload["is_safe"]),
                            feedback=option_payload["feedback"],
                            score_delta=int(option_payload.get("score_delta", 0)),
                            next_step_id=option_payload.get("next_step_id"),
                            ends_attempt=bool(option_payload.get("ends_attempt", False)),
                            tags=list(option_payload.get("tags", [])),
                        )
                    )

        await db.commit()

    async def list_scenarios(self, db: AsyncSession) -> list[ScenarioCard]:
        stmt = (
            select(TrainingScenario)
            .options(
                selectinload(TrainingScenario.steps).selectinload(TrainingScenarioStep.options),
            )
            .order_by(TrainingScenario.created_at.asc(), TrainingScenario.id.asc())
        )
        scenarios = list((await db.scalars(stmt)).all())
        return [self._serialize_card(item) for item in scenarios]

    async def start_attempt(
        self,
        db: AsyncSession,
        *,
        user: User,
        scenario_id: str,
    ) -> AttemptStateOut:
        scenario = await self._require_scenario(db, scenario_id)
        attempt = TrainingAttempt(
            user_id=user.id,
            scenario_id=scenario.id,
            current_step_id=scenario.start_step_id,
            status="in_progress",
            score=0,
            hints_used=0,
        )
        db.add(attempt)
        await db.flush()

        events = [
            await self._append_event(
                db,
                attempt=attempt,
                event_name="scenario.started",
                step_id=scenario.start_step_id,
                payload={
                    "attempt_id": str(attempt.id),
                    "user_id": str(user.id),
                    "scenario_id": scenario.id,
                },
            )
        ]

        await db.commit()
        await self._publish_events(events)
        return self._serialize_state(attempt, scenario)

    async def get_attempt_state(
        self,
        db: AsyncSession,
        *,
        user: User,
        attempt_id: UUID,
    ) -> AttemptStateOut:
        attempt = await self._require_attempt(db, attempt_id, user.id)
        scenario = await self._require_scenario(db, attempt.scenario_id)
        return self._serialize_state(attempt, scenario)

    async def submit_answer(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        user: User,
        attempt_id: UUID,
        option_id: str,
    ) -> AttemptAnswerResultOut:
        attempt = await self._require_attempt(db, attempt_id, user.id)
        if attempt.status != "in_progress":
            raise self._conflict("Attempt already finished.")

        scenario = await self._require_scenario(db, attempt.scenario_id)
        current_step = self._get_step(scenario, attempt.current_step_id)
        option = self._get_option(current_step, option_id)

        next_step_id = option.next_step_id
        next_status = "in_progress"
        if option.ends_attempt:
            next_status = "failed"
            next_step_id = None
        elif option.next_step_id is None:
            next_status = "completed"

        db.add(
            TrainingAttemptAnswer(
                attempt_id=attempt.id,
                step_id=current_step.id,
                option_id=option.id,
                is_safe=option.is_safe,
                score_delta=option.score_delta,
            )
        )
        attempt.score += option.score_delta
        attempt.current_step_id = next_step_id
        attempt.status = next_status
        await db.flush()

        events = [
            await self._append_event(
                db,
                attempt=attempt,
                event_name="scenario.answer_submitted",
                step_id=current_step.id,
                payload={
                    "attempt_id": str(attempt.id),
                    "scenario_id": scenario.id,
                    "step_id": current_step.id,
                    "option_id": option.id,
                    "outcome": option.outcome,
                    "is_safe": option.is_safe,
                    "score": attempt.score,
                    "status": attempt.status,
                    "tags": list(option.tags),
                },
            )
        ]

        if attempt.status != "in_progress":
            events.extend(
                await self._finalize_attempt(
                    db,
                    redis,
                    user=user,
                    attempt=attempt,
                    scenario=scenario,
                )
            )
        else:
            await db.commit()

        await self._publish_events(events)
        refreshed_attempt = await self._require_attempt(db, attempt.id, user.id)
        state = self._serialize_state(refreshed_attempt, scenario)
        return AttemptAnswerResultOut(
            **state.model_dump(),
            answer_feedback=AnswerFeedbackOut(
                step_id=current_step.id,
                option_id=option.id,
                outcome=option.outcome,
                is_safe=option.is_safe,
                feedback=option.feedback,
                explanation=current_step.explanation,
                hint=current_step.hint,
                tags=list(option.tags),
            ),
        )

    async def use_hint(
        self,
        db: AsyncSession,
        *,
        user: User,
        attempt_id: UUID,
    ) -> HintResultOut:
        attempt = await self._require_attempt(db, attempt_id, user.id)
        if attempt.status != "in_progress":
            raise self._conflict("Attempt already finished.")

        scenario = await self._require_scenario(db, attempt.scenario_id)
        current_step = self._get_step(scenario, attempt.current_step_id)

        has_hint_event = await db.scalar(
            select(TrainingEventLog.id).where(
                TrainingEventLog.attempt_id == attempt.id,
                TrainingEventLog.step_id == current_step.id,
                TrainingEventLog.event_name == "scenario.hint_used",
            )
        )
        if has_hint_event is not None:
            raise self._conflict("Hint already used for current step.")

        attempt.hints_used += 1
        attempt.score -= self.HINT_PENALTY
        await db.flush()

        events = [
            await self._append_event(
                db,
                attempt=attempt,
                event_name="scenario.hint_used",
                step_id=current_step.id,
                payload={
                    "attempt_id": str(attempt.id),
                    "scenario_id": scenario.id,
                    "step_id": current_step.id,
                    "hint_penalty": self.HINT_PENALTY,
                    "hints_used": attempt.hints_used,
                    "score": attempt.score,
                },
            )
        ]
        await db.commit()
        await self._publish_events(events)

        state = self._serialize_state(attempt, scenario)
        return HintResultOut(
            **state.model_dump(),
            hint=current_step.hint,
            hint_penalty=self.HINT_PENALTY,
        )

    async def list_attempt_events(
        self,
        db: AsyncSession,
        *,
        user: User,
        attempt_id: UUID,
    ) -> list[AttemptEventOut]:
        attempt = await self._require_attempt(db, attempt_id, user.id)
        stmt = (
            select(TrainingEventLog)
            .where(TrainingEventLog.attempt_id == attempt.id)
            .order_by(TrainingEventLog.created_at.asc(), TrainingEventLog.id.asc())
        )
        events = list((await db.scalars(stmt)).all())
        return [
            AttemptEventOut(
                id=event.id,
                attempt_id=event.attempt_id,
                event_name=event.event_name,
                payload=event.payload,
                created_at=event.created_at,
            )
            for event in events
        ]

    async def ensure_attempt_access(
        self,
        db: AsyncSession,
        *,
        user: User,
        attempt_id: UUID,
    ) -> None:
        await self._require_attempt(db, attempt_id, user.id)

    async def _finalize_attempt(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        user: User,
        attempt: TrainingAttempt,
        scenario: TrainingScenario,
    ) -> list[dict[str, object]]:
        if attempt.progress_synced:
            return []

        max_score = self._max_score(scenario)
        positive_score = max(attempt.score, 0)
        score_percentage = round((positive_score / max_score) * 100, 2) if max_score else 0.0
        is_success = attempt.status == "completed" and attempt.score >= scenario.passing_score

        answer_lookup = {
            (answer.step_id, answer.option_id): answer
            for answer in attempt.answers
        }
        errors: list[AttemptErrorInput] = []
        for step in scenario.steps:
            for option in step.options:
                answer = answer_lookup.get((step.id, option.id))
                if answer is None or option.is_safe:
                    continue
                errors.append(
                    AttemptErrorInput(
                        error_code="unsafe_choice",
                        message=option.feedback,
                        severity="high" if option.ends_attempt else "medium",
                        penalty_points=abs(min(option.score_delta, 0)),
                        context={
                            "step_id": step.id,
                            "step_title": step.title,
                            "option_id": option.id,
                            "option_label": option.label,
                            "tags": list(option.tags),
                        },
                    )
                )

        attempt.progress_synced = True
        finished_at = datetime.now(timezone.utc)
        finished_event = await self._append_event(
            db,
            attempt=attempt,
            event_name="scenario.finished",
            step_id=None,
            payload={
                "attempt_id": str(attempt.id),
                "user_id": str(user.id),
                "scenario_id": scenario.id,
                "score": attempt.score,
                "max_score": max_score,
                "score_percentage": score_percentage,
                "success_rate": round(score_percentage / 100, 4),
                "status": attempt.status,
                "success": is_success,
            },
        )

        await progress_service.submit_attempt(
            db,
            redis,
            user=user,
            payload=ScenarioAttemptCreate(
                scenario_key=scenario.id,
                scenario_title=scenario.title,
                started_at=attempt.created_at or finished_at,
                finished_at=finished_at,
                success=is_success,
                completed=True,
                score_percentage=score_percentage,
                submission_payload={
                    "attempt_id": str(attempt.id),
                    "status": attempt.status,
                    "score": attempt.score,
                    "max_score": max_score,
                    "hints_used": attempt.hints_used,
                    "answers": [
                        {
                            "step_id": answer.step_id,
                            "option_id": answer.option_id,
                            "is_safe": answer.is_safe,
                            "score_delta": answer.score_delta,
                        }
                        for answer in attempt.answers
                    ],
                },
                errors=errors,
            ),
        )
        return [finished_event]

    async def _require_scenario(self, db: AsyncSession, scenario_id: str) -> TrainingScenario:
        stmt = (
            select(TrainingScenario)
            .options(
                selectinload(TrainingScenario.steps).selectinload(TrainingScenarioStep.options),
            )
            .where(TrainingScenario.id == scenario_id)
        )
        scenario = await db.scalar(stmt)
        if scenario is None:
            raise self._not_found("Scenario not found.")
        return scenario

    async def _require_attempt(
        self,
        db: AsyncSession,
        attempt_id: UUID,
        user_id: UUID,
    ) -> TrainingAttempt:
        stmt = (
            select(TrainingAttempt)
            .options(selectinload(TrainingAttempt.answers))
            .where(
                TrainingAttempt.id == attempt_id,
                TrainingAttempt.user_id == user_id,
            )
        )
        attempt = await db.scalar(stmt)
        if attempt is None:
            raise self._not_found("Attempt not found.")
        return attempt

    async def _append_event(
        self,
        db: AsyncSession,
        *,
        attempt: TrainingAttempt,
        event_name: str,
        step_id: str | None,
        payload: dict[str, object],
    ) -> dict[str, object]:
        event = TrainingEventLog(
            attempt_id=attempt.id,
            step_id=step_id,
            event_name=event_name,
            payload=payload,
        )
        db.add(event)
        await db.flush()
        created_at = event.created_at or datetime.now(timezone.utc)
        return {
            "id": event.id,
            "attempt_id": str(event.attempt_id),
            "event_name": event.event_name,
            "payload": event.payload,
            "created_at": created_at.isoformat(),
        }

    async def _publish_events(self, events: list[dict[str, object]]) -> None:
        for event in events:
            await attempt_event_broker.publish(str(event["attempt_id"]), event)

    def _serialize_card(self, scenario: TrainingScenario) -> ScenarioCard:
        return ScenarioCard(
            id=scenario.id,
            title=scenario.title,
            level=scenario.level,
            setting=scenario.setting,
            summary=scenario.summary,
            threat_types=list(scenario.threat_types),
            steps_count=len(scenario.steps),
            passing_score=scenario.passing_score,
        )

    def _serialize_state(self, attempt: TrainingAttempt, scenario: TrainingScenario) -> AttemptStateOut:
        current_step = self._get_step(scenario, attempt.current_step_id) if attempt.current_step_id else None
        answers = attempt.__dict__.get("answers") or []
        answered_steps = len(answers)
        total_steps = len(scenario.steps)
        progress_percent = int((answered_steps / total_steps) * 100) if total_steps else 0

        return AttemptStateOut(
            attempt_id=attempt.id,
            user_id=attempt.user_id,
            scenario=ScenarioMeta(
                id=scenario.id,
                title=scenario.title,
                level=scenario.level,
                setting=scenario.setting,
                summary=scenario.summary,
                threat_types=list(scenario.threat_types),
                passing_score=scenario.passing_score,
            ),
            status=attempt.status,
            score=attempt.score,
            hints_used=attempt.hints_used,
            answered_steps=answered_steps,
            total_steps=total_steps,
            progress_percent=progress_percent,
            current_step=(
                StepOut(
                    id=current_step.id,
                    title=current_step.title,
                    prompt=current_step.prompt,
                    has_hint=bool(current_step.hint),
                    options=[
                        StepOptionOut(id=option.id, label=option.label)
                        for option in current_step.options
                    ],
                )
                if current_step
                else None
            ),
        )

    def _get_step(self, scenario: TrainingScenario, step_id: str | None) -> TrainingScenarioStep:
        if step_id is None:
            raise self._bad_request("Attempt has no active step.")
        for step in scenario.steps:
            if step.id == step_id:
                return step
        raise self._bad_request("Attempt has no active step.")

    def _get_option(self, step: TrainingScenarioStep, option_id: str) -> TrainingStepOption:
        for option in step.options:
            if option.id == option_id:
                return option
        raise self._bad_request("Option not found for current step.")

    def _max_score(self, scenario: TrainingScenario) -> int:
        return sum(
            max(max((option.score_delta for option in step.options), default=0), 0)
            for step in scenario.steps
        )

    def _not_found(self, detail: str) -> Exception:
        from fastapi import HTTPException, status

        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    def _bad_request(self, detail: str) -> Exception:
        from fastapi import HTTPException, status

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    def _conflict(self, detail: str) -> Exception:
        from fastapi import HTTPException, status

        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


scenario_gameplay_service = ScenarioGameplayService()
