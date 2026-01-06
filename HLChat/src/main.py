from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from adapter.input.api import message, user
from common.mongo import getMonoDB
from config import mysql_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SessionFactory = None
mongoDB = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongoDB, SessionFactory

    mongoDB = getMonoDB()
    mongoDB.connect()
    print("Connected to MongoDB")

    engine = create_engine(mysql_url, echo=True)  # echo=True: SQL을 로그로 찍는 옵션
    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("Connected to MySQL")

    yield

    engine.dispose()
    print("Disconnected to MySQL")

    mongoDB.disconnect()
    print("Disconnected to MongoDB")

app = FastAPI(lifespan=lifespan)
app.include_router(message.router)
app.include_router(user.router)
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