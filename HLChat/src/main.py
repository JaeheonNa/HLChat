from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from adapter.input.api import message
from common.mongo import MongoDB, getMonoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongoDB = getMonoDB()
    mongoDB.connect()
    print("Connected to MongoDB")
    yield
    mongoDB.disconnect()
    print("Disconnected to MongoDB")

app = FastAPI(lifespan=lifespan)
app.include_router(message.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def health_check_handler():
    return {"ping": "pong"}