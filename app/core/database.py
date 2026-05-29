from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.core.config import settings

# Базовый класс для моделей
Base = declarative_base()

# Создание асинхронного движка
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Логирование SQL
    pool_size=settings.DB_POOL_SIZE,  # Размер пула соединений
    max_overflow=settings.DB_MAX_OVERFLOW,  # Макс. дополнительных соединений
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Таймаут получения соединения
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздание соединений через час
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не устаревать объекты после коммита
    autocommit=False,
    autoflush=False,
)

# Dependency для получения сессии
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии БД для FastAPI зависимостей"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Автоматический коммит при успехе
        except Exception:
            await session.rollback()  # Откат при ошибке
            raise
        finally:
            await session.close()  # Закрытие сессии

# Функции для управления жизненным циклом
async def init_db():
    """Инициализация БД (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Закрытие соединений"""
    await engine.dispose()