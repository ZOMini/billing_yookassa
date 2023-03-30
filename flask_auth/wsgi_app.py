# import logging

from gevent import monkey

result = monkey.patch_all()
# logging.error('--- INFO --- gevent result is %s', result)

from app import app

# app.logger.error('--- INFO --- gevent result is %s', result)
