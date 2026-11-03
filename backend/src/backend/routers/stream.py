import asyncio
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from backend.config import FRONTEND_ORIGIN
from backend.market import simulate_tick
from backend.pricing import prices

router = APIRouter()

TICK_SECONDS = 1.0


@router.websocket("/ws/prices")
async def stream_prices(websocket: WebSocket) -> None:
    origin = websocket.headers.get("origin")
    if origin != FRONTEND_ORIGIN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    current_prices = dict(prices)  # make a copy of the prices dict
    rng = random.Random()
    try:
        while True:
            current_prices = simulate_tick(current_prices, rng)
            await websocket.send_json(current_prices)
            await asyncio.sleep(TICK_SECONDS)
    except WebSocketDisconnect:
        pass
