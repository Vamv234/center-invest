from __future__ import annotations

import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            if user_id not in self._connections:
                return
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                self._connections.pop(user_id, None)

    async def broadcast_to_user(self, user_id: UUID, payload: dict[str, object]) -> None:
        sockets = list(self._connections.get(user_id, set()))
        for socket in sockets:
            try:
                await socket.send_json(payload)
            except (RuntimeError, WebSocketDisconnect, OSError):
                await self.disconnect(user_id, socket)


websocket_manager = WebSocketManager()
