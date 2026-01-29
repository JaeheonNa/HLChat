from abc import ABC, abstractmethod

from fastapi import UploadFile

from domain.response import FileSchema


class SaveFileUsecase(ABC):
    @abstractmethod
    async def saveFile(self, file: UploadFile, room_id: str, sender_id: str, message_type: str) -> FileSchema:
        pass

class FindFileUsecase(ABC):
    @abstractmethod
    async def findFile(self, file_id: int, access_token: str) -> FileSchema:
        pass