import datetime
import enum
import uuid

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from db_conn import Base


class NotificationTypesEnum(enum.Enum):
    user_create = "user_create"
    change_password = "change_password"
    new_films = "new_films"
    received_likes = "received_likes"


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                unique=True,
                nullable=False)
    notification_type = Column(Enum(NotificationTypesEnum), nullable=False)
    notification_text = Column(String(511), nullable=True)
    notification_data = Column(DateTime, default=datetime.datetime.now())
    status = Column(Boolean, default=False, nullable=False)  # Выполнено ли. Т.е. если True то отправлено.
    ready = Column(Boolean, default=False, nullable=False)  # Готово ли к отправке.
    user_id = Column(UUID(as_uuid=True))
    user_name = Column(String(127), nullable=True)
    user_email = Column(String(127), nullable=True)  # В нашем случае email, все описанные "notification_type", на данный момент, для работы с email.

    def __init__(self, user_id: UUID,
                 notification_type: str,
                 notification_text: str| None = None,
                 user_name: str | None = None,
                 user_email: str | None = None,
                 status: bool = False,
                 ready: bool = False):
        self.user_id = user_id
        self.notification_type = notification_type
        self.notification_text = notification_text
        self.user_name = user_name
        self.user_email = user_email
        self.status = status
        self.ready = ready


class AdminNotifEvent(Base):
    __tablename__ = 'adminnotifevent'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                unique=True,
                nullable=False)
    notification_type = Column(Enum(NotificationTypesEnum), nullable=False)
    notification_text = Column(String(511), nullable=True)
    notification_data = Column(DateTime, default=datetime.datetime.now())
    status = Column(Boolean, default=False, nullable=False)
    user_ids = Column(ARRAY(String(63)))

    def __init__(self, user_ids: list,
                 notification_type: str,
                 notification_text: str | None = None,
                 ready: bool = False):
        self.user_ids = user_ids
        self.notification_type = notification_type
        self.notification_text = notification_text
        self.ready = ready
