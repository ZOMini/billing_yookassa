import datetime
import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Interval,
    String
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Relationship
from sqlalchemy.sql import func

from db.pg import Base, engine


class Currency(enum.Enum):
    rub = 'RUB'
    usd = 'USD'


class StatusEnum(enum.Enum):
    succeeded = "succeeded"
    canceled = "canceled"
    pending = "pending"
    refund = "refund"


class UserStatus(Base):
    __tablename__ = 'userstatus'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=False), default=None, nullable=True)
    actual = Column(Boolean, default=False)  # Если True, то подписка выдана. "Флаг" для воркера.
    expires_status = Column(Boolean, default=False)  # Если True, то воркер отправил сообщение о скором окончании подписки.
    payments = Relationship("PaymentPG", back_populates="userstatus")

    def __repr__(self) -> str:
        return str(self.id)


class Tariff(Base):
    __tablename__ = 'tariff'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    days = Column(Interval(), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(127), nullable=False)
    payments = Relationship("PaymentPG", back_populates="tariff")

    def __repr__(self) -> str:
        return str(self.id)


class PaymentPG(Base):
    __tablename__ = 'payment'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    payment = Column(String(127), nullable=False)
    income = Column(Float, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    tariff_id = Column(UUID(as_uuid=True), ForeignKey("tariff.id"))
    tariff = Relationship("Tariff", back_populates="payments")
    userstatus_id = Column(UUID(as_uuid=True), ForeignKey("userstatus.id"))
    userstatus = Relationship("UserStatus", back_populates="payments")

    def __repr__(self) -> str:
        return str(self.id)


async def test_data():
    tariff = Tariff(id='ffe0d805-3595-4cc2-a892-f2bedbec4ac1',
                    days=datetime.timedelta(30),
                    price=100.0,
                    description='Покупка подписки на 30 дней.')
    async with AsyncSession(engine) as session:
        try:
            session.add(tariff)
            await session.commit()
        except IntegrityError:
            await session.rollback()
