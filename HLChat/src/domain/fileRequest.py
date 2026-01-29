from pydantic import BaseModel

class DownloadFileRequest(BaseModel):
    file_id: int