from mobius.api.server import start_server
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import requests
import websockets
import json
import subprocess

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
            async with websockets.connect(f'ws://{self.url[7:]}/do') as websocket:
                await websocket.send(json.dumps(data))  # Convert dictionary to JSON
                response = await websocket.recv()  # Receive response from server
                print(f"Server response: {response}")
        print("WEBSOCKET")
        websocket_client()

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