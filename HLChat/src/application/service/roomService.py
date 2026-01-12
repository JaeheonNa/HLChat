from fastapi import Depends
from typing_extensions import override

from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from application.port.input.roomUsecase import FindRoomIdUsecase
from application.port.output.roomPort import MongoRoomPort


class FindRoomIdService(FindRoomIdUsecase):

    def __init__(self, roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)):
        self.roomPort = roomPort

    @override
    async def findRoomIdByUserIdAndFriendId(self,
                                      user_id: str,
                                      friend_id: str
    ):
        return await self.roomPort.findRoomIdByUserIdAndFriendId(user_id, friend_id)