from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.payment_repository import PaymentRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.user_repository import UserRepository
from app.core.webhook_security import verify_signature
from app.schemas.payment import PaymentCreate
from app.schemas.webhook import WebhookRequest
from app.utils import messages


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction_repo = PaymentRepository(db)
        self.account_repo = AccountRepository(db)
        self.user_repo = UserRepository(db)

    async def process_webhook(self, webhook_data: WebhookRequest) -> dict:
        data_dict = webhook_data.dict()
        if not verify_signature(data_dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.webhook_invalid_signature
            )

        existing = await self.transaction_repo.get_by_transaction_id(webhook_data.transaction_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=messages.webhook_transaction_already_processed
            )

        user = await self.user_repo.get_user_by_id(webhook_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.webhook_user_not_found
            )

        account = await self.account_repo.get_or_create_account_by_user(webhook_data.user_id, webhook_data.account_id)

        await self.account_repo.add_balance(account.id, webhook_data.amount)

        transaction = await self.transaction_repo.create_payment(
            PaymentCreate(
                transaction_id=webhook_data.transaction_id,
                account_id=account.id,
                amount=webhook_data.amount
            )
        )

        return {
            "status": messages.success,
            "message": messages.webhook_payment_processed_successfully,
            "transaction_id": transaction.transaction_id,
            "new_balance": account.balance + webhook_data.amount
        }