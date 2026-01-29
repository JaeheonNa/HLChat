from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from adapter.input.api import message, user, room, file
from common.exceptions import BasicException
from common.mongo import getMonoDB
from common.mysql import getMySqlDB

mongoDB = None
mysqlDB = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongoDB, mysqlDB

    mongoDB = getMonoDB()
    mongoDB.connect()

    mysqlDB = getMySqlDB()
    mysqlDB.connect()

    yield

    mysqlDB.disconnect()
    print("Disconnected from MySQL")

    mongoDB.disconnect()
    print("Disconnected from MongoDB")

app = FastAPI(lifespan=lifespan)
app.include_router(message.router)
app.include_router(user.router)
app.include_router(room.router)
app.include_router(file.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    # [중요] 이 부분이 있어야 프론트에서 파일명 헤더를 읽을 수 있음
    expose_headers=["Content-Disposition"]
)

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}

@app.exception_handler(BasicException)
async def basic_exception_handler(request: Request, exc: BasicException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.now().isoformat(),
            "error_code": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )