from pydantic import BaseModel, field_validator
from decimal import Decimal


class WebhookRequest(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v


class WebhookResponse(BaseModel):
    status: str
    message: str
    transaction_id: str