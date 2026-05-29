from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountResponse


class AccountService:
    def __init__(self, db: AsyncSession):
        self.account_repository = AccountRepository(db)

    async def create_account(self, new_account: AccountCreate) -> Account:
        return await self.account_repository.create_account(new_account)

    async def find_accounts(self, user_id: int) -> List[AccountResponse]:
        accounts: List[Account] = await self.account_repository.get_accounts_by_user_id(user_id)

        return [AccountResponse.model_validate(account, from_attributes=True) for account in accounts]

    async def soft_delete_accounts(self, user_id: int) -> None:
        await self.account_repository.soft_delete_account(user_id)
