from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "<EMAIL>",
                    "password": "<PASSWORD>"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # Время жизни токена в секундах