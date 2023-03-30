import logging

from core.config import settings
from db.db import db_session, init_db
from models.db_models import Role, User


def create_superuser():
    if (not db_session.query(Role.query.filter(Role.role == 'superuser').exists()).scalar()
            and not db_session.query(User.query.filter(User.name == settings.SUPERUSER_NAME).exists()).scalar()):
        superuser = User(settings.SUPERUSER_NAME,
                         settings.SUPERUSER_EMAIL,
                         settings.SUPERUSER_PASSWORD)
        db_session.add(superuser)
        superrole = Role('superuser')
        db_session.add(superrole)
        db_session.commit()
        superuser.role.append(superrole)
        db_session.commit()
        logging.error('--- INFO --- Superuser created, email and password in .env')
        # Ниже для биллинга.
        subscriber = Role('subscriber')
        db_session.add(subscriber)
        db_session.commit()
    else:
        logging.error('--- INFO --- Superuser exist. Aborted.')


if __name__ == '__main__':
    init_db()
    create_superuser()
