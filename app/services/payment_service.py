from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentBase, PaymentCreate, PaymentResponse
from app.services.account_service import AccountService


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repository = PaymentRepository(db)

    async def create_payment(self, new_payment: PaymentCreate) -> PaymentResponse:
        return PaymentResponse.model_validate(
            await self.payment_repository.create_payment(new_payment), from_attributes=True
        )

    async def get_payments(self, user_id: int) -> List[PaymentResponse]:
        return [
            PaymentResponse.model_validate(payment, from_attributes=True) for payment in
                await self.payment_repository.get_payments(
                    await self.__get_account_ids(user_id)
                )
        ]

    async def soft_delete_payments(self, user_id: int) -> None:
        await self.payment_repository.soft_delete_payment(
            await self.__get_account_ids(user_id)
        )

    async def __get_account_ids(self, user_id: int) -> List[int]:
        account_service = AccountService(self.db)
        return [account.id for account in await account_service.find_accounts(user_id)]