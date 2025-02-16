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
    filename="do.log",   # Log file name
    level=logging.INFO,    # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@router.websocket("/do")
async def websocket_listener(websocket: WebSocket):
    from mobius.api import server_state
    await websocket.accept()
    logging.info("WebSocket connection accepted")
    logging.info(server_state['full_attach_ip'])

    try:
        # Receive JSON-ified request from the WebSocket client
        data = await websocket.receive_text()
        if not data.strip():  # Check if empty message received
            raise ValueError("Received empty message")
        request = json.loads(data)  # Convert JSON string to dict
        logging.info(f"Received data: {request}")
        # Validate required fields
        required_keys = {"type", "natural_language_task"}
        if not all(k in request for k in required_keys):
            await websocket.send_text(json.dumps({"error": "Invalid request format"}))
            return

        identifier = request.get("identifier", None)
        if identifier is None and server_state['full_attach_ip']:
            identifier = server_state['full_attach_ip']
        else:
            print("this wasn't meant to happen lol")
            return

        # Check if a task is already running on this device
        if identifier in active_tasks:
            await websocket.send_text(json.dumps({"error": "Can't start simultaneous actions on the same device."}))
            return
        # Select appropriate handler
        if request["type"] == "wifi":
            handler = ADBWifiHandler(ip=identifier)
        elif request["type"] == "local":
            handler = ADBLocalHandler(device_id=identifier)
        else:
            await websocket.send_text(json.dumps({"error": "Invalid handler type"}))
            return
        # Create and store the active task
        task = ActiveTask(handler, websocket, request["natural_language_task"], request.get("human_in_loop", False))
        active_tasks[identifier] = task

        # Execute the task asynchronously
        await execute(task)
        logging.info("/do: execution finished")
        del active_tasks[identifier]
        await websocket.close()


    except WebSocketDisconnect:
        logging.info(f"Device {identifier} disconnected.")
        active_tasks.pop(identifier, None)  # Remove safely if exists

    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
        logging.error("Received invalid JSON format")

    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
        logging.error(f"Error processing request: {e}")