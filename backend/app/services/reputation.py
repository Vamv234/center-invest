from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ReputationReason
from app.models.reputation import ReputationLedger
from app.models.user import User
from app.services.rating import rating_service


@dataclass(slots=True)
class ReputationComputation:
    delta: int
    reason: ReputationReason
    description: str
    context: dict[str, object]


class ReputationService:
    REGISTRATION_BONUS = 50
    SUCCESS_BASE = 25
    FAILURE_BASE = -15
    PERSONAL_BEST_BONUS = 5
    FARMING_PENALTY = -5
    ATTEMPT_DELTA_MIN = -40
    ATTEMPT_DELTA_MAX = 60

    def calculate_attempt_delta(
        self,
        *,
        scenario_key: str,
        success: bool,
        score_percentage: float,
        previous_best_score: float,
        previous_completion_count: int,
        error_penalty_points: int,
    ) -> ReputationComputation:
        delta = 0
        breakdown: list[str] = []

        if success:
            delta += self.SUCCESS_BASE
            breakdown.append(f"Успешное прохождение: +{self.SUCCESS_BASE}")

            score_bonus = min(int(score_percentage // 10), 10)
            if score_bonus:
                delta += score_bonus
                breakdown.append(f"Бонус за процент: +{score_bonus}")

            if previous_best_score > 0 and score_percentage >= previous_best_score + 10:
                delta += self.PERSONAL_BEST_BONUS
                breakdown.append(f"Улучшение рекорда: +{self.PERSONAL_BEST_BONUS}")

            if previous_completion_count >= 2:
                delta += self.FARMING_PENALTY
                breakdown.append(f"Штраф за фарм: {self.FARMING_PENALTY}")
            reason = ReputationReason.SCENARIO_SUCCESS
            description = f"Сценарий {scenario_key} пройден"
        else:
            delta += self.FAILURE_BASE
            breakdown.append(f"Провал сценария: {self.FAILURE_BASE}")
            reason = ReputationReason.SCENARIO_FAILURE
            description = f"Сценарий {scenario_key} завершён с ошибками"

        if error_penalty_points:
            capped_penalty = min(error_penalty_points, 30)
            delta -= capped_penalty
            breakdown.append(f"Штраф за ошибки: -{capped_penalty}")

        delta = max(self.ATTEMPT_DELTA_MIN, min(self.ATTEMPT_DELTA_MAX, delta))
        return ReputationComputation(
            delta=delta,
            reason=reason,
            description=description,
            context={
                "scenario_key": scenario_key,
                "score_percentage": score_percentage,
                "breakdown": breakdown,
            },
        )

    async def apply_delta(
        self,
        db: AsyncSession,
        *,
        user: User,
        delta: int,
        reason: ReputationReason,
        description: str,
        scenario_key: str | None = None,
        attempt_id: UUID | None = None,
        context: dict[str, object] | None = None,
    ) -> ReputationLedger:
        actual_delta = delta
        if delta < 0:
            actual_delta = max(-user.reputation_score, delta)

        user.reputation_score += actual_delta
        user.league = rating_service.league_for_score(user.reputation_score)

        event = ReputationLedger(
            user_id=user.id,
            attempt_id=attempt_id,
            scenario_key=scenario_key,
            delta=actual_delta,
            balance_after=user.reputation_score,
            reason=reason,
            description=description,
            context=context or {},
        )
        db.add(event)
        await db.flush()
        return event

    async def award_registration_bonus(self, db: AsyncSession, user: User) -> ReputationLedger:
        return await self.apply_delta(
            db,
            user=user,
            delta=self.REGISTRATION_BONUS,
            reason=ReputationReason.REGISTRATION_BONUS,
            description="Бонус за регистрацию",
            context={"bonus": self.REGISTRATION_BONUS},
        )


reputation_service = ReputationService()
