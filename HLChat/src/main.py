from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from adapter.input.api import message, user
from common.mongo import getMonoDB
from common.mysql import getMySqlDB
from config import mysql_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

mongoDB = None
mysqlDB = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongoDB, mysqlDB

    mongoDB = getMonoDB()
    mongoDB.connect()
    print("Connected to MongoDB")

    mysqlDB = getMySqlDB()
    mysqlDB.connect()
    print("Connected to MySQL")

    yield

    mysqlDB.disconnect()
    print("Disconnected from MySQL")

    mongoDB.disconnect()
    print("Disconnected from MongoDB")

app = FastAPI(lifespan=lifespan)
app.include_router(message.router)
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:9000"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}