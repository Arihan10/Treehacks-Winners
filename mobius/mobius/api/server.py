from fastapi import FastAPI
from mobius.api.routes import do_router
import subprocess
import time

app = FastAPI()

import threading
import uvicorn
import time
import contextlib
"""
Run this to debug with postman

def run_server():
    uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=8000)

def start_server():
    print("Starting FastAPI server on http://127.0.0.1:8000")
    run_server()
"""
import traceback
import sys
port = 8000
def run_server():
    uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=port)
    # with open('SERVER_OUT.TXT', 'a', buffering=1) as f:  # Open in append mode, line-buffered
    #     with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):  # Redirect both stdout and stderr
    #         try:
    #             print("TEST TEST TEST SERVER OUT")
    #             uvicorn.run("mobius.api.server:app", host="127.0.0.1", port=port)
    #         except Exception as e:
    #             print("ERROR OCCURRED:", e)
    #             traceback.print_exc()  # Print full traceback to file
    #             raise  # Optional: Re-raise for external handling


def start_server(full_attach_ip: str = None):
    from mobius.api import server_state
    server_state['full_attach_ip'] = full_attach_ip

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give the server some time to start
    time.sleep(2)

    return f'http://127.0.0.1:{port}'


app.include_router(do_router)

