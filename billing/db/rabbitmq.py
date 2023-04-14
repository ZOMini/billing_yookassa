import pika

from core.config import settings

credentials = pika.PlainCredentials(username=settings.RABBIT_USER, password=settings.RABBIT_PASS)


def rabbit_conn(credentials=credentials):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBIT_HOST, credentials=credentials))
    return connection
