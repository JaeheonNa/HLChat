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
            userDomain: UserDomain = UserDomain(
                userId=user.user_id,
                password=user.password,
                username=user.user_name,
                active=user.active,
                email=user.email,
                phone=user.phone,
                phone_verified=user.phone_verified,
                profile_image=user.profile_image,
                provider=user.provider or 'LOCAL',
                provider_id=user.provider_id,
                password_changed_at=user.password_changed_at,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            return userDomain
        else:
            return None

    @override
    async def findAllUsers(self) -> List[UserSchema]:
        users = self.session.scalars(select(User).where(User.active == True))
        return [UserSchema.model_validate(user) for user in users]

    @override
    async def findUsersByUserIds(self, user_id_list: List[str]) -> List[UserDomain] | None:
        users: List[User] = self.session.scalars(select(User)
                                                       .where(User.user_id.in_(user_id_list))
                                                       .where(User.active == True))
        return [UserDomain(userId=user.user_id, username=user.user_name, password=None, active=True) for user in users]

    @override
    async def findUserByProviderId(self, provider: str, provider_id: str) -> UserDomain | None:
        user: User = self.session.scalar(
            select(User).where(User.provider == provider, User.provider_id == provider_id)
        )
        if user is not None:
            userDomain: UserDomain = UserDomain(
                userId=user.user_id,
                password=user.password,
                username=user.user_name,
                active=user.active,
                email=user.email,
                phone=user.phone,
                phone_verified=user.phone_verified,
                profile_image=user.profile_image,
                provider=user.provider or 'LOCAL',
                provider_id=user.provider_id,
                password_changed_at=user.password_changed_at,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            return userDomain
        else:
            return None

    @override
    async def findUserByNameAndPhone(self, user_name: str, phone: str) -> UserDomain | None:
        user: User = self.session.scalar(
            select(User).where(User.user_name == user_name, User.phone == phone, User.active == True)
        )
        if user is not None:
            userDomain: UserDomain = UserDomain(
                userId=user.user_id,
                password=user.password,
                username=user.user_name,
                active=user.active,
                email=user.email,
                phone=user.phone,
                phone_verified=user.phone_verified,
                profile_image=user.profile_image,
                provider=user.provider or 'LOCAL',
                provider_id=user.provider_id,
                password_changed_at=user.password_changed_at,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            return userDomain
        else:
            return None
