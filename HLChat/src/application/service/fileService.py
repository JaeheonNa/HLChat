import os
import shutil
import uuid
from typing import override

from fastapi import Depends, UploadFile, HTTPException

from adapter.output.filePersistenceAdapter import RequestFilePersistenceAdapter
from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from application.port.input.fileUsecase import SaveFileUsecase, FindFileUsecase
from application.port.output.filePort import MariaFilePort
from application.port.output.roomPort import MongoRoomPort
from domain.fileDomain import FileDomain
from domain.orm import File
from domain.response import FileSchema
from domain.roomDomain import RoomDomain
from domain.userDomain import UserDomain


class SaveFileService(SaveFileUsecase):
    def __init__(self,
                 mariaFilePort: MariaFilePort = Depends(RequestFilePersistenceAdapter)
    ):
        self.mariaFilePort = mariaFilePort

    @override
    async def saveFile(self, file: UploadFile, room_id: str, sender_id: str, message_type: str) -> FileSchema:
        fileDomain: FileDomain = FileDomain(file, room_id, sender_id, message_type)
        fileId = await self.mariaFilePort.saveFileUploadHistory(fileDomain)
        fileDomain.save(fileId)
        return await self.mariaFilePort.updateFileUploadHistory(fileDomain)

class FindFileService(FindFileUsecase):
    def __init__(self,
                 mariaFilePort: MariaFilePort = Depends(RequestFilePersistenceAdapter),
                 mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)):
        self.mariaFilePort = mariaFilePort
        self.mongoRoomPort = mongoRoomPort

    @override
    async def findFile(self, fileId: int, access_token: str) -> FileSchema:
        userId: str = UserDomain.decodeJWT(access_token)
        file: FileSchema = await self.mariaFilePort.findFileByFileId(fileId)
        room: RoomDomain = await self.mongoRoomPort.findRoomByRoomId(file.roomId)

        if (userId not in room.members):
            raise HTTPException(status_code=401, detail="Not Authorized")

        return file