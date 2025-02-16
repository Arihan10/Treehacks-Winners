from fastapi import FastAPI
from mobius.api.routes import do_router
import subprocess
import time

app = FastAPI()

import threading
import uvicorn
import time

"""
Run this to debug with postman

def run_server():
    uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=8000)

def start_server():
    print("Starting FastAPI server on http://127.0.0.1:8000")
    run_server()
"""

def run_server(port):
    uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=port)

def start_server():
    port = 8000
    run_server(port)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give the server some time to start
    time.sleep(2)

    return f'http://127.0.0.1:{port}'


app.include_router(do_router)

