from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, account: AccountCreate) -> Account:
        new_account = Account(
            user_id = account.user_id,
            balance = account.balance,
            currency = account.currency
        )

        self.db.add(new_account)
        await self.db.flush()
        await self.db.refresh(new_account)
        return new_account

    async def get_accounts_by_user_id(self, user_id: int) -> List[Account]:
        accounts = await self.db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return list(accounts.scalars().all())

    async def get_account_by_id(self, account_id: int) -> Account:
        result = await self.db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_account_by_user(self, user_id: int, account_id: int) -> Account:
        """Получить или создать счет для пользователя (без указания ID извне)"""
        account: Account = await self.get_account_by_id(account_id)
        if account and account.user_id == user_id:
            return account

        account = Account(
            user_id=user_id,
            balance=Decimal("0.00"),
            currency="RUB"
        )
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def add_balance(self, account_id: int, amount: Decimal) -> None:
        """Начисление баланса"""
        await self.db.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + amount)
        )
        await self.db.flush()

    async def soft_delete_account(self, user_id: int) -> None:
        accounts = await self.get_accounts_by_user_id(user_id)

        if not accounts:
            return

        for account in accounts:
            account.deleted_at = datetime.now()

        await self.db.commit()
