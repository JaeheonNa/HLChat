from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import message

app = FastAPI(redirect_slashes=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",  # Quasar 개발 서버
        "http://127.0.0.1:9000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(message.router)

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}