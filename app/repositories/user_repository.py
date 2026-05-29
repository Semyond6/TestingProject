from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models.user import User
from app.schemas.user import UserRegister, UserUpdateRequest
from app.utils import messages


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: UserRegister) -> User:
        new_user = User(
            full_name=user.full_name,
            email=user.email,
            hashed_password=security.hash_password(user.password)
        )
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def is_exists_user(self, user: UserRegister) -> bool:
        user = await self.db.execute(
            select(User).where(User.full_name == user.full_name, User.email == user.email)
        )
        return user.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.db.execute(
            select(User).where(User.email == email)
        )
        return user.scalar_one_or_none()

    async def update_user(self, update_user: UserUpdateRequest) -> User:
        user = await self.db.execute(
            select(User).where(User.id == update_user.id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail=messages.user_not_found)

        if update_user.full_name:
            user.full_name = update_user.full_name
        if update_user.email:
            user.email = update_user.email
        if update_user.password:
            if not security.verify_password(update_user.password, user.hashed_password):
                user.hashed_password = security.hash_password(update_user.password)

        await self.db.commit()
        await self.db.refresh(user)

        return user


    async def get_users(self) -> List[User]:
        users = await self.db.execute(
            select(User)
        )
        return list(users.scalars().all())

    async def delete_user(self, user_id: int) -> None:
        await self.db.execute(
            delete(User).where(User.id == user_id)
        )
        await self.db.commit()

    async def soft_delete_user(self, user_id: int) -> None:
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail=messages.user_not_found)

        user.is_active = False
        user.deleted_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(user)