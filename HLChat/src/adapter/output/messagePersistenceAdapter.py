from typing import Any

from fastapi import Depends
from typing_extensions import override
from datetime import datetime

from application.port.output.messagePort import MongoMessagePort
from common.mongo import MongoDB
from domain.odm import HLChatMessage
from domain.messageRequest import SendMessageRequest
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
        newMessageLnNo = await self.find_message_ln_no(request)
        if request.message_type == "str":
            new_message = HLChatMessage(room_id=request.room_id,
                                        message_ln_no=newMessageLnNo,
                                        sender=request.sender_id,
                                        message=request.message,
                                        message_type=request.message_type,
                                        file_id=None,
                                        created_at=datetime.now())
        else:
            new_message = HLChatMessage(room_id=request.room_id,
                                        message_ln_no=newMessageLnNo,
                                        sender=request.sender_id,
                                        message=request.message,
                                        message_type=request.message_type,
                                        file_id=request.file_id,
                                        file_path=request.file_path,
                                        created_at=datetime.now())
        await self.mongo_db.save(new_message)
        return newMessageLnNo

    @override
    async def findSavedMessage(self, room_id: int, message_ln_no: int | None = None):

        if message_ln_no is None:
            messages = await self.mongo_db.find(HLChatMessage,
                                               HLChatMessage.room_id == room_id,
                                               sort=HLChatMessage.message_ln_no.desc(),
                                               limit=50)
            return messages
        else:
            messages = await self.mongo_db.find(HLChatMessage,
                                                HLChatMessage.room_id == room_id,
                                                HLChatMessage.message_ln_no < message_ln_no,
                                                sort=HLChatMessage.message_ln_no.desc(),
                                                limit=50)
            return messages