import datetime
import enum
import logging
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Interval,
    String,
    select
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Relationship, joinedload, selectinload
from sqlalchemy.sql import func

from db.pg import Base, async_session, engine, get_pg


class StatusEnum(enum.Enum):
    succeeded = "succeeded"
    canceled = "canceled"
    pending = "pending"


class UserStatus(Base):
    __tablename__ = 'userstatus'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    subscriber = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), default=None, nullable=True)
    actual = Column(Boolean, default=False)
    payments = Relationship("PaymentPG", back_populates="userstatus")


class Tariff(Base):
    __tablename__ = 'tariff'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    days = Column(Interval(), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(127), nullable=False)
    payments = Relationship("PaymentPG", back_populates="tariff")


class PaymentPG(Base):
    __tablename__ = 'payment'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    # user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # expires_at = Column(DateTime(timezone=True), server_default=(func.now() + func.make_interval(0, 0, 0, 30)))
    payment = Column(String(127), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    tariff_id = Column(UUID(as_uuid=True), ForeignKey("tariff.id"))
    tariff = Relationship("Tariff", back_populates="payments")
    userstatus_id = Column(UUID(as_uuid=True), ForeignKey("userstatus.id"))
    userstatus = Relationship("UserStatus", back_populates="payments")


async def test_data():
    tariff = Tariff(id='ffe0d805-3595-4cc2-a892-f2bedbec4ac1',
                  days=datetime.timedelta(30),
                  price=100.0,
                  description='Покупка подписки на 30 дней.')
    # userstatus = UserStatus(id='ffe0d805-3595-4cc2-a892-f2bedbec4ac9')
    # payment = PaymentPG(id='ffe0d805-3595-4cc2-a892-f2bedbec4ac2',
    #                     user_id='ffe0d805-3595-4cc2-a892-f2bedbec4ac3',
    #                     payment='qq11',
    #                     status='canceled',
    #                     tariff = tariff,
    #                     userstatus = userstatus)
    async with AsyncSession(engine) as session:
        try:
            session.add(tariff)
            await session.commit()
        except IntegrityError:
            await session.rollback()
        # try:
        #     session.add(userstatus)
        #     await session.commit()
        # except IntegrityError:
        #     await session.rollback()
        # try:
        #     session.add(payment)
        #     await session.commit()
        # except IntegrityError:
        #     await session.rollback()
        # try:
        #     session.add(payment)
        #     await session.commit()
        # except IntegrityError:
        #     await session.rollback()
        # stmt = select(UserStatus)
        # us1 = await session.scalars(stmt)
        # us2 = us1.one_or_none()
        # logging.error('AAAAAAAAAAAAAAAA us2 %s', us2.id)
        # stmt = select(PaymentPG)
        # p1 = await session.scalars(stmt)
        # p2 = p1.one_or_none()
        # logging.error('AAAAAAAAAAAAAAAA p2 %s', p2.userstatus.id)
        # # p2.userstatus_id.append(p2)
        # await session.commit()
        # stmt = select(UserStatus).options(joinedload(UserStatus.payments))
        # qq11 = await session.scalars(stmt)
        # qq22 = qq11.first()
        # logging.error('AAAAAAAAAAAAAAAA qq33 %s', qq22.payments[0].id)
