from abc import abstractmethod, ABC
from typing import List

from domain.orm import User

class MariaUserPort(ABC):
    @abstractmethod
    async def saveUser(self, user: User) -> User:
        pass

    @abstractmethod
    async def findUserByUserId(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    async def findAllUsers(self) -> List[User]:
        pass