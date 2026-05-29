import asyncio
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.account import Account


async def init_test_data():
    """Создание тестовых данных"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "test@gmail.com"))
        existing = result.scalar_one_or_none()

        if existing:
            print("Test data already exists")
            return

        test_user = User(
            full_name="Test User",
            email="test@gmail.com",
            hashed_password=hash_password("Test123456"),
            is_admin=False,
            is_active=True
        )
        session.add(test_user)
        await session.flush()

        test_account = Account(
            user_id=test_user.id,
            balance=0.00,
            currency="RUB"
        )
        session.add(test_account)

        admin_user = User(
            full_name="Admin User",
            email="admin@gmail.com",
            hashed_password=hash_password("Admin123456"),
            is_admin=True,
            is_active=True
        )
        session.add(admin_user)
        await session.flush()

        await session.commit()

        print("Test data created successfully:")
        print(f"  Test user: test@gmail.com / Test123456")
        print(f"  Admin user: admin@gmail.com / Admin123456")


async def main():
    """Инициализация БД"""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Creating test data...")
    await init_test_data()

    print("Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(main())