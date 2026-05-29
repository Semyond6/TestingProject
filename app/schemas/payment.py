from decimal import Decimal
from typing import List

from pydantic import BaseModel


class PaymentBase(BaseModel):
    transaction_id: str
    amount: Decimal

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "transaction_id": "",
                    "amount": Decimal("0.00"),
                }
            ]
        }
    }

class PaymentCreate(PaymentBase):
    account_id: int

class PaymentResponse(PaymentBase):
    account_id: int

class PaymentsResponse(BaseModel):
    payments: List[PaymentResponse]
