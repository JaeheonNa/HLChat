from abc import ABC, abstractmethod
from typing import List, Optional

from domain.odm import HLChatReaction
from domain.reactionRequest import ToggleReactionRequest


class MongoReactionPort(ABC):
    @abstractmethod
    async def findReaction(self, room_id: int, message_ln_no: int, reaction_type: str, user_id: str) -> Optional[HLChatReaction]:
        pass

    @abstractmethod
    async def saveReaction(self, request: ToggleReactionRequest) -> HLChatReaction:
        pass

    @abstractmethod
    async def deleteReaction(self, reaction: HLChatReaction) -> None:
        pass

    @abstractmethod
    async def findReactionsByMessage(self, room_id: int, message_ln_no: int) -> List[HLChatReaction]:
        pass

    @abstractmethod
    async def findReactionsByRoom(self, room_id: int) -> List[HLChatReaction]:
        pass
