import datetime
import enum
import uuid

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.pg import Base


class StatusEnum(enum.Enum):
    succeeded = "succeeded"
    canceled = "canceled"
    pending = "pending"


class PaymentPG(Base):
    __tablename__ = 'billing'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    expires_at = Column(DateTime(timezone=False),
                        server_default=(func.now() + func.make_interval(0, 0, 0, 30)))
    amount = Column(Float, nullable=False)
    payment = Column(String(127), nullable=False)
    status = Column('value', Enum(StatusEnum), nullable=False)
    role_granted = Column(Boolean, default=False, nullable=False)
