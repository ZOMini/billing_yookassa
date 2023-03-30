import hashlib
import uuid
from hmac import compare_digest

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.config import settings as SETT
from db.db import Base

# many_to_many связывающая таблица.
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete='CASCADE'),
           primary_key=True), extend_existing=True
)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    auth = relationship('Auth', order_by='Auth.data_time',
                        back_populates='user', cascade='all, delete, delete-orphan')
    role = relationship('Role', secondary=user_role, back_populates='user')

    def __init__(self, name: str, email: str, password: str):
        self.name = name
        self.email = email
        self.password = self.password_hash(password, email)

    def __repr__(self):
        return f'<User {self.name}>'

    def password_hash(self, password: str, email: str) -> str:
        '''Функция хеширует пароль(sha256 + стат. соль + дин. соль).'''
        pw_hash = hashlib.sha256((password + SETT.SALT_PASSWORD + email).encode('utf-8')).hexdigest()
        return pw_hash

    def check_password(self, password: str, email: str) -> bool:
        '''Функция сравнивает пароли - нехешированный(in param) с хешированным(в базе).'''
        return compare_digest(self.password_hash(password, email), self.password)


def create_partition(target, connection, **kw) -> None:
    import datetime as dt
    now_year = dt.datetime.utcnow().year
    # На всякий -1 год, типо dump-ы старые подгружать.
    # Так же можно усложнить, делать по месяцам например.
    for year in range(now_year - 1, now_year + 2):
        connection.execute(
            """CREATE TABLE IF NOT EXISTS "auth_%s" PARTITION OF "auth" FOR VALUES FROM ('%s-01-01') TO ('%s-12-31')""", year, year, year
        )


class Auth(Base):
    __tablename__ = 'auth'
    __table_args__ = (
        {
            'postgresql_partition_by': 'RANGE (data_time)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_agent = Column(String, nullable=True)
    u_a_hash = Column(BigInteger, nullable=True)
    data_time = Column(DateTime(timezone=False), default=func.now(),
                       nullable=False, primary_key=True)  # Дата логина.
    refresh_token = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    tokens_time = Column(DateTime(timezone=False), default=func.now(),
                         onupdate=func.current_timestamp(), nullable=True)  # Дата последней выдачи ключей.
    user = relationship(User, back_populates="auth")

    def __init__(self, user_id: uuid, user_agent: str, u_a_hash: int,
                 access_token: str, refresh_token: str):
        self.user_id = user_id
        self.user_agent = user_agent
        self.u_a_hash = u_a_hash
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return f'<Auth {self.data_time} - {self.user_agent}>'


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, nullable=False)
    role = Column(String, unique=True, nullable=False)
    user = relationship("User", secondary=user_role, back_populates="role")

    def __init__(self, role: str):
        self.role = role

    def __repr__(self):
        return f'<Role {self.role}>'
