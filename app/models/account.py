from sqlalchemy import Column, Numeric, DateTime, ForeignKey, String, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from decimal import Decimal
from app.core.database import Base

from app.models.payment import Payment


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    balance = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Отношения
    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account {self.id} - Balance: {self.balance} {self.currency}>"