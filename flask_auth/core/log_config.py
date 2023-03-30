import logging

import logstash
from flask import Flask, Response, request

from core.config import settings


class RequestIdFilter(logging.Filter):
    def __init__(self, name: str | None = None, response: Response | None = None) -> None:
        self.name = name
        self.response: Response = response
    
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-Id')
        record.tags = ['auth_api']
        record.status = self.response.status_code
        record.request = request
        return True


def init_logs(app: Flask):
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('this will show in the log')
