from abc import ABC, abstractmethod
from typing import Dict, List

from domain.reactionRequest import ToggleReactionRequest


class ToggleReactionUsecase(ABC):
    @abstractmethod
    async def toggleReaction(self, request: ToggleReactionRequest) -> Dict:
        pass


class FindReactionsByMessageUsecase(ABC):
    @abstractmethod
    async def findReactionsByMessage(self, room_id: int, message_ln_no: int) -> Dict:
        pass


class FindReactionsByRoomUsecase(ABC):
    @abstractmethod
    async def findReactionsByRoom(self, room_id: int) -> Dict[int, Dict]:
        pass
