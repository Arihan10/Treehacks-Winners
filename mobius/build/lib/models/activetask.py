from fastapi import WebSocket
from adb_handler import ADBHandler

class ActiveTask:
    def __init__(self, handler: ADBHandler, websocket: WebSocket, natural_language_task: str):
        self.handler = handler
        self.websocket = websocket
        self.natural_language_task = natural_language_task
    
    async def send_message(self, message: str):
        await self.websocket.send_text(message)
        return await self.receive_message()
    
    async def receive_message(self):
        return await self.websocket.receive_text()