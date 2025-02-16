from fastapi import FastAPI
from mobius.api.routes import do_router
import subprocess
import time

app = FastAPI()

import threading
import uvicorn
import time

def run_server():
    uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=8000)

def start_server():
    print("Starting FastAPI server on http://127.0.0.1:8000")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give the server some time to start
    time.sleep(2)

    return "http://127.0.0.1:8000"


app.include_router(do_router)

