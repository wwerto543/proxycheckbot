import os
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Получаем путь к базе из переменной окружения хостинга или используем локальный путь
SHARED_DIR = os.getenv('SHARED_DIR', '/app/shared')
DB_URL = f"sqlite+aiosqlite:///{SHARED_DIR}/proxy_bot.db"

Base = declarative_base()

class User(Base):
    """Модель пользователя с расширенными полями для статистики и контроля доступа."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False) # Telegram ID
    username = Column(String, nullable=True)
    
    # Статусы: 'pending' (новый), 'approved' (подписан), 'banned' (заблокирован)
    status = Column(String, default="pending")
    
    # Флаг администратора (для тебя)
    is_admin = Column(Boolean, default=False)
    
    # Время регистрации
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Дата последней активности (для статистики в админке)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Инициализация движка
engine = create_async_engine(DB_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """Функция создания таблиц при запуске бота."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Генератор сессий для работы с БД."""
    async with async_session() as session:
        yield session