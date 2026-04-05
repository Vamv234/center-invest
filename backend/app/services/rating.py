from __future__ import annotations

import json

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.enums import League
from app.models.reputation import ReputationLedger
from app.models.user import User


class RatingService:
    LEAGUE_THRESHOLDS: tuple[tuple[League, int], ...] = (
        (League.BRONZE, 0),
        (League.SILVER, 200),
        (League.GOLD, 500),
        (League.PLATINUM, 900),
        (League.DIAMOND, 1400),
    )

    def league_for_score(self, score: int) -> League:
        current_league = League.BRONZE
        for league, threshold in self.LEAGUE_THRESHOLDS:
            if score >= threshold:
                current_league = league
        return current_league

    def next_league(self, score: int) -> tuple[League | None, int | None]:
        for league, threshold in self.LEAGUE_THRESHOLDS:
            if score < threshold:
                return league, threshold - score
        return None, None

    async def get_user_rank(self, db: AsyncSession, user: User) -> int:
        higher_rank_stmt = select(func.count(User.id)).where(
            User.is_active.is_(True),
            or_(
                User.reputation_score > user.reputation_score,
                and_(
                    User.reputation_score == user.reputation_score,
                    User.created_at < user.created_at,
                ),
            ),
        )
        higher_rank_count = await db.scalar(higher_rank_stmt)
        return int(higher_rank_count or 0) + 1

    async def invalidate_leaderboard_cache(self, redis: Redis) -> None:
        try:
            async for key in redis.scan_iter(match="rating:leaderboard:*"):
                await redis.delete(key)
        except RedisError:
            return

    async def get_leaderboard(
        self,
        db: AsyncSession,
        redis: Redis,
        *,
        limit: int,
        offset: int,
    ) -> dict[str, object]:
        cache_key = f"rating:leaderboard:{limit}:{offset}"
        try:
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except RedisError:
            cached = None

        total_stmt = select(func.count(User.id)).where(User.is_active.is_(True))
        total = int(await db.scalar(total_stmt) or 0)

        leaderboard_stmt = (
            select(User)
            .where(User.is_active.is_(True))
            .order_by(desc(User.reputation_score), asc(User.created_at))
            .offset(offset)
            .limit(limit)
        )
        users = (await db.scalars(leaderboard_stmt)).all()
        items = [
            {
                "rank": offset + index,
                "user_id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "reputation_score": user.reputation_score,
                "league": user.league.value,
            }
            for index, user in enumerate(users, start=1)
        ]
        payload = {"items": items, "total": total, "limit": limit, "offset": offset}

        try:
            await redis.setex(
                cache_key,
                settings.leaderboard_cache_ttl_seconds,
                json.dumps(payload),
            )
        except RedisError:
            pass
        return payload

    async def get_rating_overview(self, db: AsyncSession, user: User) -> dict[str, object]:
        next_league, points_to_next = self.next_league(user.reputation_score)
        recent_events_stmt = (
            select(ReputationLedger)
            .where(ReputationLedger.user_id == user.id)
            .order_by(desc(ReputationLedger.created_at))
            .limit(10)
        )
        recent_events = (await db.scalars(recent_events_stmt)).all()
        return {
            "user_id": user.id,
            "reputation_score": user.reputation_score,
            "league": user.league,
            "rank": await self.get_user_rank(db, user),
            "next_league": next_league,
            "points_to_next_league": points_to_next,
            "recent_events": recent_events,
        }


rating_service = RatingService()
