from fastapi import FastAPI
from .routes import do_router

app = FastAPI()

def start_server():
    import uvicorn
    print("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

    return "http://127.0.0.1:8000"

app.include_router(do_router)