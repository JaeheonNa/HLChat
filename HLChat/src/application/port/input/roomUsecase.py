from abc import ABC, abstractmethod


class FindRoomIdUsecase(ABC):

    @abstractmethod
    async def findRoomIdByUserIdAndFriendId(self,
                                      user_id: str,
                                      friend_id: str
    ):
        pass

