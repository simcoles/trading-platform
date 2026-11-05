from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from backend.broadcaster import broadcaster
from backend.config import FRONTEND_ORIGIN

router = APIRouter()


@router.websocket("/ws/prices")
async def stream_prices(websocket: WebSocket) -> None:
    origin = websocket.headers.get("origin")
    if origin != FRONTEND_ORIGIN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    queue = broadcaster.subscribe()
    try:
        await websocket.send_json(broadcaster.current_prices)
        while True:
            prices = await queue.get()
            await websocket.send_json(prices)
    except WebSocketDisconnect:
        pass
    finally:
        broadcaster.unsubscribe(queue)
