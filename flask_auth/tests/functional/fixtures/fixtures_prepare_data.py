import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from core.config import settings as SETT
from models.db_models import Auth, Role, User
from tests.functional.test_data.api_users import (
    user_admin,
    user_change_pwd,
    user_delete_role,
    user_good_token,
    user_login,
    user_logout,
    user_new,
    user_new_existing,
    user_new_role,
    user_refresh
)

DATA_BASE = f'postgresql://{SETT.POSTGRES_USER}:{SETT.POSTGRES_PASSWORD}@{SETT.DB_DOCKER_HOST}/{SETT.POSTGRES_DB}'

engine = create_engine(DATA_BASE, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_users():
    init_db()
    db_session.query(Auth).delete()
    db_session.query(Role).delete()
    db_session.query(User).delete()
    db_session.commit()
    admin_role = Role('admin')
    db_session.add(admin_role)
    db_session.commit()
    for user in (
            user_new_existing,
            user_change_pwd,
            user_good_token,
            user_login,
            user_admin,
            user_logout,
            user_refresh,
            user_new_role,
            user_delete_role
    ):

        new_user = User(user['name'],
                        user['email'],
                        user['password'])
        db_session.add(new_user)

        if user['role'] == 'admin':
            role = db_session.query(Role).filter(Role.role == 'admin').one_or_none()
            new_user.role.append(role)
            db_session.commit()
    yield
    db_session.query(Auth).delete()
    db_session.query(Role).delete()
    db_session.query(User).delete()
    db_session.commit()
