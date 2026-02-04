from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from typing_extensions import override

from application.port.output.reactionPort import MongoReactionPort
from common.mongo import MongoDB, getMonoDB
from domain.odm import HLChatReaction
from domain.reactionRequest import ToggleReactionRequest


class RequestReactionPersistenceAdapter(MongoReactionPort):
    def __init__(self, mongo_db: MongoDB = Depends(getMonoDB)):
        self.mongo_db = mongo_db.engine

    @override
    async def findReaction(self, room_id: int, message_ln_no: int, reaction_type: str, user_id: str) -> Optional[HLChatReaction]:
        reactions = await self.mongo_db.find(
            HLChatReaction,
            HLChatReaction.room_id == room_id,
            HLChatReaction.message_ln_no == message_ln_no,
            HLChatReaction.reaction_type == reaction_type,
            HLChatReaction.user_id == user_id,
            limit=1
        )
        return reactions[0] if reactions else None

    @override
    async def saveReaction(self, request: ToggleReactionRequest) -> HLChatReaction:
        new_reaction = HLChatReaction(
            room_id=request.room_id,
            message_ln_no=request.message_ln_no,
            reaction_type=request.reaction_type,
            user_id=request.user_id,
            user_name=request.user_name,
            created_at=datetime.now()
        )
        await self.mongo_db.save(new_reaction)
        return new_reaction

    @override
    async def deleteReaction(self, reaction: HLChatReaction) -> None:
        await self.mongo_db.delete(reaction)

    @override
    async def findReactionsByMessage(self, room_id: int, message_ln_no: int) -> List[HLChatReaction]:
        reactions = await self.mongo_db.find(
            HLChatReaction,
            HLChatReaction.room_id == room_id,
            HLChatReaction.message_ln_no == message_ln_no
        )
        return reactions

    @override
    async def findReactionsByRoom(self, room_id: int) -> List[HLChatReaction]:
        reactions = await self.mongo_db.find(
            HLChatReaction,
            HLChatReaction.room_id == room_id
        )
        return reactions
