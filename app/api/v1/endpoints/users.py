from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.deps import DBSession, CurrentUserId, CurrentAdminId
from app.schemas.account import AccountsResponse
from app.schemas.auth import TokenResponse, LoginRequest
from app.schemas.payment import PaymentsResponse
from app.schemas.user import UserRegister, UserUpdateRequest, UserResponse, UsersDataResponse
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.services.payment_service import PaymentService
from app.services.user_service import UserService
from app.utils import messages

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def user_register(user_data: UserRegister, db: DBSession):
    user_service = UserService(db)
    return await user_service.create_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
        login_data: LoginRequest,
        db: DBSession
):
    """
    Авторизация пользователя по email и password.

    - **email**: Email пользователя
    - **password**: Пароль

    Возвращает JWT токен для дальнейшей аутентификации
    """
    auth_service = AuthService(db)

    try:
        token = await auth_service.authenticate_user(login_data)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.auth_incorrect_email_or_password,
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============= ПОЛЬЗОВАТЕЛЬСКИЕ ЭНДПОИНТЫ =============


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: CurrentUserId, db: DBSession):
    user_service = UserService(db)
    return await user_service.find_user_by_id(user_id)

@router.get("/me/accounts", response_model=AccountsResponse)
async def get_current_user_accounts(current_user: CurrentUserId, db: DBSession):
    account_service = AccountService(db)
    return AccountsResponse(accounts=await account_service.find_accounts(current_user))

@router.get("/me/payments", response_model=PaymentsResponse)
async def get_current_user_payments(current_user: CurrentUserId, db: DBSession):
    payment_service = PaymentService(db)
    return PaymentsResponse(payments=await payment_service.get_payments(current_user))


# ============= АДМИНСКИЕ ЭНДПОИНТЫ =============


@router.get("/users", response_model=UsersDataResponse)
async def get_users(admin: CurrentAdminId, db: DBSession):
    user_service = UserService(db)
    return UsersDataResponse(users=await user_service.get_users())

@router.get("/users/{user_id}/accounts", response_model=AccountsResponse)
async def get_user_accounts(user_id: int, admin: CurrentAdminId, db: DBSession):
    account_service = AccountService(db)
    return AccountsResponse(accounts=await account_service.find_accounts(user_id))

@router.get("/users/{user_id}/payments", response_model=PaymentsResponse)
async def get_user_payments(user_id: int, admin: CurrentAdminId, db: DBSession):
    payment_service = PaymentService(db)
    return PaymentsResponse(payments=await payment_service.get_payments(user_id))

@router.put("/users", response_model=UserResponse)
async def update_user(admin: CurrentAdminId, user: UserUpdateRequest, db: DBSession):
    user_service = UserService(db)
    return await user_service.update_user(user)

@router.delete("/users/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, admin: CurrentAdminId, db: DBSession):
    user_service = UserService(db)
    await user_service.delete_user(user_id)

@router.delete("/users/{user_id}")
async def soft_delete_user(user_id: int, admin: CurrentAdminId, db: DBSession):
    user_service = UserService(db)
    await user_service.soft_delete_user(user_id)

