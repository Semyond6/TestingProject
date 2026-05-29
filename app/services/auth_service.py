from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.security import verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings
from app.utils import messages


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.db = db

    async def authenticate_user(self, login_data: LoginRequest) -> Optional[TokenResponse]:
        """Аутентификация пользователя и выдача токена"""
        user = await self.user_repo.get_user_by_email(login_data.email)

        if not user:
            return None

        if not verify_password(login_data.password, user.hashed_password):
            return None

        if not user.is_active:
            raise ValueError(messages.auth_user_account_disabled)

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin}
        )

        return TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )