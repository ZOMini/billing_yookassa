from flask_swagger_ui import get_swaggerui_blueprint as swaggerui

from core.config import app
from docs.v1.config import API_URL, CONFIG, SWAGGER_URL
from docs.v1.routes import swagger


def init_docs():
    app.register_blueprint(swagger, url_prefix=SWAGGER_URL)
    app.register_blueprint(swaggerui(SWAGGER_URL, API_URL, CONFIG))
