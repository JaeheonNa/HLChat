from fastapi import FastAPI
from api import message

app = FastAPI()

app.include_router(message.router)

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}