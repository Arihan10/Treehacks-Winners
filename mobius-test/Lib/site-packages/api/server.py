from fastapi import FastAPI
app = FastAPI()

mobile = Mobile()

@app.get("/")
async def root():
    mobile.do("mobile made on server")
    return {"message": "Hello World"}

def start_server():
    import uvicorn
    print("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

    return "http://127.0.0.1:8000"