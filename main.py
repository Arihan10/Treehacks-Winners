from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from mobius import Mobius
from typing import Dict
from routes import do_router

app = FastAPI()

mobile = Mobius().create()

@app.get("/")
async def root():
    mobile.do("mobile made on server")
    return {"message": "Hello World"}

app.include_router(do_router)
