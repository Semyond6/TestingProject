from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


class PaymentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_payment(self, payment: PaymentCreate) -> Payment:
        payment = Payment(**payment.dict())

        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_payments(self, account_ids: list[int]) -> List[Payment]:
        payments = await self.db.execute(
            select(Payment).where(Payment.account_id.in_(account_ids))
        )
        return list(payments.scalars().all()) if payments else []

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def soft_delete_payment(self, account_ids: list[int]) -> None:
        payments = await self.get_payments(account_ids)

        if not payments:
            return

        for payment in payments:
            payment.deleted_at = datetime.now()

        await self.db.commit()
