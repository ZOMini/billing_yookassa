import os
import sys

# Для дебага.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(f'{BASE_DIR}\\flask_auth')

# from core.tracer import configure_tracer

# configure_tracer()

from flask import Response, request
from flask_migrate import Migrate

from api.v1.auth import auth
from api.v1.oauth import oauth
from api.v1.role import role
from core.config import app, settings
from core.log_config import init_logs
from core.oauth import init_oauth
# from core.tracer import init_tracer
from db.db import DATA_BASE, db_session, init_db
from docs.app import init_docs
from services.jwt import *  # Регистрируем JWT

init_db()
app.register_blueprint(role, url_prefix="/auth/api/v1")
app.register_blueprint(auth, url_prefix="/auth/api/v1")
app.register_blueprint(oauth, url_prefix="/auth/api/v1")
app.config['SQLALCHEMY_DATABASE_URI'] = DATA_BASE
migrate = Migrate(app, db_session)
init_docs()
init_oauth(app)
# init_tracer(app)
init_logs(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.after_request
def add_request_id_and_logging(response: Response):
    # app.logger.addFilter(RequestIdFilter('RequestIdFilter', response))
    # app.logger.info(request.get_data())
    return response


if settings.DEBUG:
    from create_superuser import create_superuser
    create_superuser()


def main():
    app.run()


if __name__ == '__main__':
    main()
