from typing import override, List

from fastapi import Depends
from sqlalchemy.orm import Session

from application.port.output.userPort import MariaUserPort
from common.mysql import getMySqlSession
from domain.orm import User
from sqlalchemy import select

from domain.response import UserSchema
from domain.userDomain import UserDomain


class RequestUserPersistenceAdapter(MariaUserPort):

    def __init__(self,
                 session: Session = Depends(getMySqlSession)
    ):
        self.session = session

    @override
    async def saveUser(self, userDomain: UserDomain) -> UserSchema:
        user: User = userDomain.toEntity()
        mergedUser: User = self.session.merge(user)
        self.session.flush() # insert는 수행하지만 commit은 수행하지 않음.
        self.session.refresh(mergedUser)
        return UserSchema.model_validate(mergedUser)

    @override
    async def findUserByUserId(self, user_id: str) -> UserDomain | None:
        user: User = self.session.scalar(select(User).where(User.user_id == user_id))
        if user is not None:
            userDomain: UserDomain = UserDomain(userId=user.user_id,
                                                password=user.password,
                                                username=user.user_name,
                                                active=user.active)
            return userDomain
        else:
            return None

    @override
    async def findAllUsers(self) -> List[UserSchema]:
        users = self.session.scalars(select(User))
        return [UserSchema.model_validate(user) for user in users]