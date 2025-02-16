from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from mobius.models import ActiveTask, DoRequest
from typing import Dict
from mobius.functionality.adb_handler import ADBWifiHandler, ADBLocalHandler
from mobius.functionality.dummy_agent import execute
import json

router = APIRouter()

active_tasks: Dict[str, ActiveTask] = {}

import logging

logging.basicConfig(
    filename="what.log",   # Log file name
    level=logging.INFO,    # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@router.websocket("/do")
async def websocket_listener(websocket: WebSocket):
    await websocket.accept()

    logging.info("RECEIVED")

    try:
        # Receive JSON-ified request from the WebSocket client
        data = await websocket.receive_text()
        request = json.loads(data)  # Convert JSON string to Python dict

        # Validate request
        if "identifier" not in request or "type" not in request or "natural_language_task" not in request:
            raise HTTPException(status_code=400, detail="Invalid request format.")

        # Check if a task is already running on this device
        if request["identifier"] in active_tasks:
            await websocket.send_text(json.dumps({"error": "Can't start simultaneous actions on the same device."}))
            return
        
        # Select appropriate handler based on type
        if request["type"] == "wifi":
            handler = ADBWifiHandler(ip=request["identifier"])
        elif request["type"] == "local":
            handler = ADBLocalHandler(device_id=request["identifier"])
        else:
            raise ValueError("Invalid handler type")
        
        # Create an active task and store it
        task = ActiveTask(handler, websocket, request["natural_language_task"], request.get("human_in_loop", False))
        active_tasks[request["identifier"]] = task

        # Execute the task asynchronously
        await execute(task)

    except WebSocketDisconnect:
        print(f"Device {request['identifier']} disconnected.")
        active_tasks.pop(request["identifier"], None)  # Remove task safely

    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        print(f"Error processing request: {e}")
