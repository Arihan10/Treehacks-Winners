from fastapi import FastAPI
from mobius import Mobius

app = FastAPI()

mobile = Mobius().create()


@app.get("/")
async def root():
    mobile.do("mobile made on server")
    return {"message": "Hello World"}
