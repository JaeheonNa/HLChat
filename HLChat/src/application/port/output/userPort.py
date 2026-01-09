from abc import abstractmethod, ABC
from typing import List

from domain.orm import User
from domain.response import UserSchema
from domain.userDomain import UserDomain


class MariaUserPort(ABC):
    @abstractmethod
    async def saveUser(self, userDomain: UserDomain) -> UserSchema:
        pass

    @abstractmethod
    async def findUserByUserId(self, user_id: str) -> UserDomain | None:
        pass

    @abstractmethod
    async def findAllUsers(self) -> List[UserSchema]:
        pass