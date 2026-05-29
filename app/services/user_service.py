from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister, UserResponse, UserUpdateRequest
from app.services.account_service import AccountService
from app.services.payment_service import PaymentService
from app.utils import messages


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def create_user(self, user: UserRegister) -> UserResponse:
        if await self.repository.is_exists_user(user):
            raise HTTPException(status_code=400, detail=messages.user_already_exists)
        new_user: User = await self.repository.create_user(user)
        return UserResponse.model_validate(new_user, from_attributes=True)

    async def find_user_by_id(self, user_id: int) -> UserResponse:
        user: User = await self.repository.get_user_by_id(user_id)
        return UserResponse.model_validate(user, from_attributes=True)

    async def update_user(self, update_user: UserUpdateRequest) -> UserResponse:
        return UserResponse.model_validate(await self.repository.update_user(update_user), from_attributes=True)

    async def get_users(self) -> List[UserResponse]:
        users = await self.repository.get_users()
        return [UserResponse.model_validate(user, from_attributes=True) for user in users]

    async def soft_delete_user(self, user_id: int) -> None:
        account_service = AccountService(self.db)
        payment_service = PaymentService(self.db)

        await self.repository.soft_delete_user(user_id)
        await account_service.soft_delete_accounts(user_id)
        await payment_service.soft_delete_payments(user_id)

    async def delete_user(self, user_id: int) -> None:
        await self.repository.delete_user(user_id)
