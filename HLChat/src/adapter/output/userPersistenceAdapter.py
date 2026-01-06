from typing import override

from fastapi import Depends
from sqlalchemy.orm import Session

from application.port.output.userPort import MariaUserPort
from common.maria import get_db
from domain.orm import User
from sqlalchemy import select


class RequestUserPersistenceAdapter(MariaUserPort):

    def __init__(self,
                 session: Session = Depends(get_db)
    ):
        self.session = session

    @override
    async def saveUser(self, user: User) -> User:
        self.session.add(user)
        self.session.flush() # insert는 수행하지만 commit은 수행하지 않음.
        self.session.refresh(user)
        return user

    @override
    async def findUserByUserId(self, user_id: str) -> User | None:
        return self.session.scalar(select(User).where(User.user_id == user_id))

    @override
    async def findAllUsers(self) -> list[User]:
        return list(self.session.scalars(select(User)))