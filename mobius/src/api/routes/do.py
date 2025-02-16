from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from ...models import ActiveTask, DoRequest
from typing import Dict
from ...functionality.adb_handler import ADBWifiHandler, ADBLocalHandler
from ...functionality.dummy_agent import execute

router = APIRouter()

active_tasks: Dict[str, ActiveTask] = {}

@router.post("/do")
async def do_action(request: DoRequest, websocket: WebSocket):
    await websocket.accept()

    if request.identifier in active_tasks:
        raise HTTPException(status_code=400, detail="Can't start simultaneous actions on the same device.")

    if request.type == "wifi":
        handler = ADBWifiHandler(ip=request.identifier)
    elif request.type == "local":
        handler = ADBLocalHandler(device_id=request.identifier)
    else:
        raise ValueError("Invalid handler type")
    
    task = ActiveTask(handler, websocket, request.natural_language_task)
    active_tasks[request.identifier] = task

    try:
        await execute(task)
    except WebSocketDisconnect:
        del active_tasks[request.identifier]
        print(f"Device {request.identifier} disconnected.")

    return {"status": "success", "handler": request.type, "identifier": request.identifier}
