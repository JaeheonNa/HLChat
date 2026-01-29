from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from application.port.output.filePort import MariaFilePort
from common.mysql import getMySqlSession
from domain.fileDomain import FileDomain
from domain.orm import File
from domain.response import FileSchema


class RequestFilePersistenceAdapter(MariaFilePort):
    def __init__(self,
                 session: Session = Depends(getMySqlSession)):
        self.session = session

    async def saveFileUploadHistory(self, fileDomain: FileDomain) -> int:
        file: File = fileDomain.toEntity()
        self.session.add(file)
        self.session.flush()  # insert는 수행하지만 commit은 수행하지 않음.
        self.session.refresh(file)
        return file.file_id

    async def updateFileUploadHistory(self, fileDomain: FileDomain) -> FileSchema:
        file: File = self.session.scalar(select(File).where(File.file_id == fileDomain.file_id))
        file.file_path = fileDomain.file_path
        mergedFile: File = self.session.merge(file)
        self.session.flush()
        self.session.refresh(mergedFile)
        return FileSchema.model_validate(mergedFile)

    async def findFileByFileId(self, fileId: int) -> FileSchema:
        file: File = self.session.scalar(select(File).where(File.file_id == fileId))
        return FileSchema.model_validate(file)
