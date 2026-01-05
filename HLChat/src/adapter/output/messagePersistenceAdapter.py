from typing import Any

from fastapi import Depends
from typing_extensions import override
from datetime import datetime

from application.port.output.messagePort import MongoMessagePort
from common.mongo import MongoDB
from domain.odm import HLChatMessage
from domain.request import SendMessageRequest
from common.mongo import getMonoDB


class RequestMessagePersistenceAdapter(MongoMessagePort):
    def __init__(self, mongo_db: MongoDB = Depends(getMonoDB)):
        self.mongo_db = mongo_db.engine

    async def find_message_ln_no(self, request: SendMessageRequest)-> int:
        message = await self.mongo_db.find(HLChatMessage,
                                           HLChatMessage.room_id == request.room_id,
                                           sort=HLChatMessage.message_ln_no.desc(),
                                           limit=1)
        if message:
            return message[0].message_ln_no + 1
        else:
            return 1

    @override
    async def saveMessage(self, request: SendMessageRequest):
        new_message_ln_no = await self.find_message_ln_no(request)
        print("new_message_ln_no: ", new_message_ln_no)
        new_message = HLChatMessage(room_id=request.room_id,
                                message_ln_no=new_message_ln_no,
                                sender=request.sender_id,
                                message=request.message,
                                created_at=datetime.now())
        await self.mongo_db.save(new_message)

    @override
    async def findSavedMessage(self, room_id: int):
        messages = await self.mongo_db.find(HLChatMessage,
                                           HLChatMessage.room_id == room_id,
                                           sort=HLChatMessage.message_ln_no.asc(),
                                           limit=50)
        return messages
