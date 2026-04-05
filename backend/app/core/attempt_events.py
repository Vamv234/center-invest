from __future__ import annotations

import asyncio
from collections import defaultdict


class AttemptEventBroker:
    def __init__(self) -> None:
        self._subscriptions: dict[str, set[asyncio.Queue[dict[str, object]]]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def publish(self, attempt_id: str, payload: dict[str, object]) -> None:
        async with self._lock:
            queues = list(self._subscriptions.get(attempt_id, set()))

        for queue in queues:
            queue.put_nowait(payload)

    async def subscribe(self, attempt_id: str) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        async with self._lock:
            self._subscriptions[attempt_id].add(queue)
        return queue

    async def unsubscribe(self, attempt_id: str, queue: asyncio.Queue[dict[str, object]]) -> None:
        async with self._lock:
            subscriptions = self._subscriptions.get(attempt_id)
            if not subscriptions:
                return
            subscriptions.discard(queue)
            if not subscriptions:
                self._subscriptions.pop(attempt_id, None)


attempt_event_broker = AttemptEventBroker()
