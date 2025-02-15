from fastapi import FastAPI
from mobius import Mobile

app = FastAPI()

mobile = Mobile()

@app.get("/")
async def root():
    mobile.do("mobile made on server")
    return {"message": "Hello World"}