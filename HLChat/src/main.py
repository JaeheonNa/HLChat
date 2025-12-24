from fastapi import FastAPI, Body, HTTPException, Depends
from schema.request import SendMessageRequest
from service import MessageService
app = FastAPI()

@app.post("/HLChat", status_code=200)
def sendMessage(request: SendMessageRequest):
    MessageService.sendMessage(request)