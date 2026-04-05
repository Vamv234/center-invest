from __future__ import annotations

from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.websocket import websocket_manager
from app.models.progress import ScenarioAttempt, ScenarioAttemptError, ScenarioProgress
from app.models.user import User
from app.schemas.progress import ScenarioAttemptCreate
from app.services.rating import rating_service
from app.services.reputation import reputation_service


class ProgressService:
    async def submit_attempt(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        user: User,
        payload: ScenarioAttemptCreate,
    ) -> dict[str, object]:
        progress = await db.scalar(
            select(ScenarioProgress).where(
                ScenarioProgress.user_id == user.id,
                ScenarioProgress.scenario_key == payload.scenario_key,
            )
        )
        if progress is None:
            progress = ScenarioProgress(
                user_id=user.id,
                scenario_key=payload.scenario_key,
                scenario_title=payload.scenario_title,
            )
            db.add(progress)
            await db.flush()

        started_at = payload.started_at or datetime.now(timezone.utc)
        finished_at = payload.finished_at or datetime.now(timezone.utc)
        completed = payload.completed if payload.completed is not None else payload.success
        duration_seconds = max(int((finished_at - started_at).total_seconds()), 0)

        attempt = ScenarioAttempt(
            user_id=user.id,
            progress_id=progress.id,
            scenario_key=payload.scenario_key,
            scenario_title=payload.scenario_title,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration_seconds,
            success=payload.success,
            completed=completed,
            score_percentage=payload.score_percentage,
            errors_count=len(payload.errors),
            submission_payload=payload.submission_payload,
        )
        db.add(attempt)
        await db.flush()

        error_penalty_points = 0
        for error in payload.errors:
            points = error.penalty_points if error.penalty_points > 0 else 3
            error_penalty_points += points
            db.add(
                ScenarioAttemptError(
                    attempt_id=attempt.id,
                    error_code=error.error_code,
                    message=error.message,
                    severity=error.severity,
                    penalty_points=points,
                    context=error.context,
                )
            )

        previous_best_score = progress.best_score
        previous_completion_count = progress.completions_count

        progress.attempts_count += 1
        progress.completions_count += int(completed)
        progress.successes_count += int(payload.success)
        progress.failures_count += int(not payload.success)
        progress.total_score += payload.score_percentage
        progress.average_score = round(progress.total_score / progress.attempts_count, 2)
        progress.best_score = max(progress.best_score, payload.score_percentage)
        progress.success_rate = round((progress.successes_count / progress.attempts_count) * 100, 2)
        progress.total_errors += len(payload.errors)
        progress.last_score = payload.score_percentage
        progress.last_result_success = payload.success
        progress.last_attempt_at = finished_at
        if completed:
            progress.last_completed_at = finished_at

        computation = reputation_service.calculate_attempt_delta(
            scenario_key=payload.scenario_key,
            success=payload.success,
            score_percentage=payload.score_percentage,
            previous_best_score=previous_best_score,
            previous_completion_count=previous_completion_count,
            error_penalty_points=error_penalty_points,
        )

        ledger = await reputation_service.apply_delta(
            db,
            user=user,
            delta=computation.delta,
            reason=computation.reason,
            description=computation.description,
            scenario_key=payload.scenario_key,
            attempt_id=attempt.id,
            context=computation.context,
        )
        attempt.reputation_delta = ledger.delta

        await db.commit()
        await rating_service.invalidate_leaderboard_cache(redis)

        refreshed_progress = await db.get(ScenarioProgress, progress.id)
        await db.refresh(refreshed_progress)
        refreshed_attempt = await db.scalar(
            select(ScenarioAttempt)
            .options(selectinload(ScenarioAttempt.errors))
            .where(ScenarioAttempt.id == attempt.id)
        )
        summary = await self.get_progress_summary(db, user)

        await websocket_manager.broadcast_to_user(
            user.id,
            {
                "type": "progress.updated",
                "summary": summary,
                "scenario_key": payload.scenario_key,
                "reputation_delta": ledger.delta,
            },
        )

        return {
            "progress": refreshed_progress,
            "attempt": refreshed_attempt,
            "summary": summary,
            "reputation_delta": ledger.delta,
        }

    async def list_progress(self, db: AsyncSession, user: User) -> list[ScenarioProgress]:
        stmt = (
            select(ScenarioProgress)
            .where(ScenarioProgress.user_id == user.id)
            .order_by(ScenarioProgress.updated_at.desc())
        )
        return list((await db.scalars(stmt)).all())

    async def get_progress_detail(
        self,
        db: AsyncSession,
        user: User,
        scenario_key: str,
    ) -> dict[str, object] | None:
        progress = await db.scalar(
            select(ScenarioProgress).where(
                ScenarioProgress.user_id == user.id,
                ScenarioProgress.scenario_key == scenario_key,
            )
        )
        if progress is None:
            return None

        attempts_stmt = (
            select(ScenarioAttempt)
            .options(selectinload(ScenarioAttempt.errors))
            .where(
                ScenarioAttempt.user_id == user.id,
                ScenarioAttempt.scenario_key == scenario_key,
            )
            .order_by(desc(ScenarioAttempt.finished_at))
            .limit(10)
        )
        attempts = list((await db.scalars(attempts_stmt)).all())
        return {"progress": progress, "recent_attempts": attempts}

    async def get_progress_summary(self, db: AsyncSession, user: User) -> dict[str, object]:
        summary_stmt = select(
            func.count(ScenarioProgress.id),
            func.coalesce(
                func.sum(case((ScenarioProgress.completions_count > 0, 1), else_=0)),
                0,
            ),
            func.coalesce(func.sum(ScenarioProgress.attempts_count), 0),
            func.coalesce(func.sum(ScenarioProgress.successes_count), 0),
            func.coalesce(func.sum(ScenarioProgress.total_score), 0.0),
            func.coalesce(func.sum(ScenarioProgress.total_errors), 0),
        ).where(ScenarioProgress.user_id == user.id)

        (
            total_scenarios,
            completed_scenarios,
            total_attempts,
            total_successes,
            total_score,
            total_errors,
        ) = (await db.execute(summary_stmt)).one()

        total_attempts = int(total_attempts or 0)
        average_success_rate = (
            round((float(total_successes or 0) / total_attempts) * 100, 2)
            if total_attempts
            else 0.0
        )
        average_score = round(float(total_score or 0) / total_attempts, 2) if total_attempts else 0.0

        return {
            "total_scenarios": int(total_scenarios or 0),
            "completed_scenarios": int(completed_scenarios or 0),
            "total_attempts": total_attempts,
            "average_success_rate": average_success_rate,
            "average_score": average_score,
            "total_errors": int(total_errors or 0),
            "reputation_score": user.reputation_score,
            "league": user.league,
        }


progress_service = ProgressService()
