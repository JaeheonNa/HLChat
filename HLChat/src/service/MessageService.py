import redis
from schema.request import SendMessageRequest
from database.mongodb import client
import datetime


def sendMessage(request: SendMessageRequest):
    db = client['local']
    room_id = request.room_id
    if request.room_id is None:
        rooms = db['rooms']
        rooms.insert_one(
            {'room_id': 'room_001',
            'message_type': request.message_type,
            'members': [request.sender_id, request.receiver_id],
            "created_at": datetime.datetime.now()}
        )
        room_id = 'room_001',

    messages = db['messages']
    messages.insert_one(
        {"room_id": room_id,
        "sender_id": request.sender_id,
        "message": request.message,
        "message_type": "text",
        "created_at": datetime.datetime.now()}
    )
