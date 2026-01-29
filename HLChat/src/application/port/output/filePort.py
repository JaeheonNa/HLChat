from abc import ABC, abstractmethod

from domain.fileDomain import FileDomain
from domain.orm import File
from domain.response import FileSchema


class MariaFilePort(ABC):
    @abstractmethod
    async def saveFileUploadHistory(self, fileDomain: FileDomain) -> int:
        pass

    @abstractmethod
    async def updateFileUploadHistory(self, fileDomain: FileDomain) -> FileSchema:
        pass

    @abstractmethod
    async def findFileByFileId(self, fileId: int) -> FileSchema:
        pass