from decimal import Decimal
from typing import List

from pydantic import BaseModel


class AccountBase(BaseModel):
    balance: Decimal
    currency: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "balance": Decimal("0.00"),
                    "currency": "RUB",
                }
            ]
        }
    }

class AccountCreate(AccountBase):
    user_id: int

class AccountResponse(AccountBase):
    user_id: int
    id: int

class AccountsResponse(BaseModel):
    accounts: List[AccountResponse]