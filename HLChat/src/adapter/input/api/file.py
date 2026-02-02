from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse

from application.port.input.fileUsecase import SaveFileUsecase, FindFileUsecase
from application.service.fileService import SaveFileService, FindFileService
from common.security import get_access_token
from domain.response import FileSchema
from domain.userDomain import UserDomain

router = APIRouter(prefix="/file")



@router.post("", status_code=201)
async def uploadFile(
        file: UploadFile = File(...),
        room_id: str = Form(...),
        sender_id: str = Form(...),
        message_type: str = Form(...),
        access_token = Depends(get_access_token),
        saveFileUsecase: SaveFileUsecase = Depends(SaveFileService)
):
    try:
        fileInfo: FileSchema = await saveFileUsecase.saveFile(file, room_id, sender_id, message_type)
        return fileInfo
    except Exception as e:
        print(f"업로드 에러: {e}")
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류 발생")

@router.get("/{file_id}/{user_id}")
async def findFileInfo(file_id: int,
                       user_id: str,
                       findFileUsecase: FindFileUsecase = Depends(FindFileService)
):
    fileSchema: FileSchema = await findFileUsecase.findFile(file_id, user_id)

    media_type: str = 'application/octet-stream'
    if fileSchema.fileName.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        media_type = f"image/{fileSchema.fileName.split('.')[-1]}"

    print(fileSchema.fileName)
    print(fileSchema.filePath)
    return FileResponse(path=fileSchema.filePath,
                        filename=fileSchema.fileName,
                        media_type=media_type)

@router.get("/down/{file_id}")
async def downloadFile(file_id: int,
                       access_token: str = Depends(get_access_token),
                       findFileUsecase: FindFileUsecase = Depends(FindFileService)
):
    userId: str = UserDomain.decodeJWT(access_token)
    fileSchema: FileSchema = await findFileUsecase.findFile(file_id, userId)

    return FileResponse(path=fileSchema.filePath,
                        filename=fileSchema.fileName,
                        media_type='application/octet-stream')