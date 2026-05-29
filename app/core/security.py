from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
from app.utils import messages

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирование и валидация JWT токена"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.auth_token_expired,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.auth_invalid_claims,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.auth_could_not_validate_credentials,
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_token_payload(payload: Dict[str, Any], require_admin: bool = False) -> int:
    """
    Валидация payload токена и извлечение user_id.

    Args:
        payload: Декодированный JWT токен
        require_admin: Требовать ли права администратора

    Returns:
        int: ID пользователя

    Raises:
        HTTPException: При невалидном токене или отсутствии прав
    """
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.auth_invalid_token_payload,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if require_admin and not payload.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.auth_admin_privileges_required,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.auth_invalid_user_id_format,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_by_valid_token(payload: Dict[str, Any]) -> int:
    """Получение user_id из токена (без проверки прав администратора)"""
    return validate_token_payload(payload, require_admin=False)


def get_admin_id_by_valid_token(payload: Dict[str, Any]) -> int:
    """Получение user_id из токена с проверкой прав администратора"""
    return validate_token_payload(payload, require_admin=True)