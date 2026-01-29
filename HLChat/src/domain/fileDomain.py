from dataclasses import field
from datetime import datetime
import os
import shutil
import uuid

from fastapi import UploadFile
from domain.orm import File

UPLOAD_DIR = "uploads"
BASE_FILE_URL = "http://localhost:8000/uploads/"

class FileDomain():
    def __init__(self, file: UploadFile, room_id: str, sender_id: str, message_type: str):
        self.file = file
        self.room_id = room_id
        self.sender_id = sender_id
        self.message_type = message_type

    def toEntity(self):
        return File(file_name=self.file.filename, room_id=self.room_id, sender_id=self.sender_id, created_at=datetime.now())

    def setId(self, fileId: int):
        self.file_id = fileId

    def save(self, fileId: int | None):
        self.file_id = fileId

        if (self.file_id == None):
            raise FileNotFoundError("File ID is not created.")

        nowDate = str(datetime.date(datetime.now()))
        file_dir = os.path.join(UPLOAD_DIR, nowDate)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        self.file_path = os.path.join(file_dir, str(self.file_id))
        with open(self.file_path, "wb") as buffer:
            shutil.copyfileobj(self.file.file, buffer)