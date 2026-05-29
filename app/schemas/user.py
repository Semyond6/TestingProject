from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.account import AccountResponse
from app.utils import messages


class UserBase(BaseModel):
    full_name: str
    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "admin",
                    "email": "<EMAIL>",
                }
            ]
        }
    }

class UserRegister(UserBase):
    password: str
    confirm_password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "admin",
                    "email": "<EMAIL>",
                    "password": "<PASSWORD>",
                    "confirm_password": "<PASSWORD>"
                }
            ]
        }
    }

    @field_validator('full_name')
    def validate_full_name(cls, value):
        if len(value) < 3:
            raise ValueError(messages.value_error_name_min_three_char)
        return value

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError(messages.value_error_pass_min_eight_char)
        if not any(c.isupper() for c in value):
            raise ValueError(messages.value_error_one_capital_letter)
        if not any(c.isdigit() for c in value):
            raise ValueError(messages.value_error_one_num)
        return value

    @field_validator('confirm_password')
    def validate_passwords_match(cls, value, values):
        if 'password' in values.data and value != values.data['password']:
            raise ValueError(messages.value_error_pass_dont_match)
        return value


class UserResponse(UserBase):
    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "full_name": "admin",
                    "email": "<EMAIL>",
                }
            ]
        }
    }

class UsersDataResponse(BaseModel):
    users: list[UserResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "full_name": "admin",
                    "email": "<EMAIL>",
                    "is_admin": True,
                }
            ]
        }
    }

class UserUpdateRequest(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "full_name": "New Name",
                    "email": "newemail@example.com",
                    "password": "NewPassword123"
                }
            ]
        }
    }
