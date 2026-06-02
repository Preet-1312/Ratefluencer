from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/progress/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await ws_manager.connect(websocket, task_id)
    try:
        # Keep connection open and listen for messages or disconnects
        while True:
            # We don't expect messages from client, but keeping loop alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, task_id)
    except Exception as e:
        print(f"WebSocket error for task {task_id}: {e}")
        ws_manager.disconnect(websocket, task_id)
