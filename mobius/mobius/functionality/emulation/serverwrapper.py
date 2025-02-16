from mobius.api.server import start_server
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import requests
import websockets
import json
import subprocess
import asyncio

def create_controller():
    return ServerWrapper()

class ServerWrapper:
    def __init__(self):
        self.url = start_server()

    def do(self, device_id, task):
        data = {
            "type": "local",
            "identifier": device_id,
            "natural_language_task": task,
            "human_in_loop": "No"
        }

        async def websocket_client():
            # Increase timeout and keepalive interval
            timeout = 600  # 10 minutes (600 seconds)
            keepalive_interval = 300  # Send a ping every 5 minutes to keep the connection alive

            try:
                async with websockets.connect(
                    f'ws://{self.url[7:]}/do', 
                    ping_interval=keepalive_interval,  # Adjust ping interval
                    ping_timeout=timeout  # Increase ping timeout
                ) as websocket:
                    await websocket.send(json.dumps(data))  # Convert dictionary to JSON
                    
                    try:
                        response = await websocket.recv()
                        print(f"Server response: {response}")
                    except websockets.exceptions.ConnectionClosedOK:
                        print("✅ WebSocket closed cleanly.")
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"⚠️ WebSocket connection closed with error: {e}")
            
            except websockets.exceptions.WebSocketException as e:
                print(f"WebSocket connection failed: {e}")

        # Run the WebSocket client
        asyncio.run(websocket_client())

    def close_all_emulators(self):
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        for line in lines:
            if line.startswith("emulator-"):
                avd_name = line.split()[0]
                try:
                    subprocess.run(["adb", "-s", avd_name, "emu", "kill"], check=True)
                    print(f"Emulator {avd_name} has been closed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error closing emulator {avd_name}: {e}")