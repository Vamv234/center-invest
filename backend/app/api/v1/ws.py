from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import resolve_access_context
from app.core.database import AsyncSessionLocal
from app.core.attempt_events import attempt_event_broker
from app.core.websocket import websocket_manager
from app.services.progress import progress_service
from app.services.scenario_gameplay import scenario_gameplay_service

router = APIRouter()


@router.websocket("/progress")
async def progress_socket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing access token")
        return

    connected = False
    user_id = None

    async with AsyncSessionLocal() as db:
        try:
            context = await resolve_access_context(token, db)
        except Exception:
            await websocket.close(code=4401, reason="Unauthorized")
            return

        user_id = context.user.id
        await websocket_manager.connect(user_id, websocket)
        connected = True
        try:
            summary = await progress_service.get_progress_summary(db, context.user)
            await websocket.send_json({"type": "progress.snapshot", "summary": summary})
            while True:
                message = await websocket.receive_text()
                if message == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({"type": "ack", "message": message})
        except WebSocketDisconnect:
            pass
        except RuntimeError:
            pass
        finally:
            if connected and user_id is not None:
                await websocket_manager.disconnect(user_id, websocket)


@router.websocket("/attempts/{attempt_id}")
async def attempt_events_socket(websocket: WebSocket, attempt_id: str) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing access token")
        return

    async with AsyncSessionLocal() as db:
        try:
            context = await resolve_access_context(token, db)
            parsed_attempt_id = UUID(attempt_id)
            await scenario_gameplay_service.ensure_attempt_access(
                db,
                user=context.user,
                attempt_id=parsed_attempt_id,
            )
        except Exception:
            await websocket.close(code=4401, reason="Unauthorized")
            return

        queue = await attempt_event_broker.subscribe(attempt_id)
        await websocket.accept()
        try:
            while True:
                queue_task = asyncio.create_task(queue.get())
                receive_task = asyncio.create_task(websocket.receive())
                done, pending = await asyncio.wait(
                    {queue_task, receive_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()

                if receive_task in done:
                    message = receive_task.result()
                    if message["type"] == "websocket.disconnect":
                        break
                    if message["type"] == "websocket.receive" and message.get("text") == "ping":
                        await websocket.send_json({"type": "pong"})

                if queue_task in done:
                    await websocket.send_json(queue_task.result())
        except WebSocketDisconnect:
            pass
        except RuntimeError:
            pass
        finally:
            await attempt_event_broker.unsubscribe(attempt_id, queue)
