from typing import Optional, Annotated, Callable, TypeVar
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.database import get_db
from app.core.security import decode_access_token, get_user_id_by_valid_token, get_admin_id_by_valid_token
from app.utils import messages

security = HTTPBearer(auto_error=False)

T = TypeVar('T', bound=Callable)


def token_dependency(validator_func: Callable[[dict], int]):
    """
    Фабрика для создания dependency из функции валидации токена.

    Args:
        validator_func: Функция для валидации payload и извлечения ID

    Returns:
        Async function для FastAPI dependency
    """

    async def dependency(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> int:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.auth_not_authenticated,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = validator_func(payload)

        return user_id

    return dependency


get_current_user_id_from_token = token_dependency(get_user_id_by_valid_token)
get_current_admin_id_from_token = token_dependency(get_admin_id_by_valid_token)


DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[int, Depends(get_current_user_id_from_token)]
CurrentAdminId = Annotated[int, Depends(get_current_admin_id_from_token)]