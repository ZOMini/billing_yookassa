import logging

import pika
from rabbit_models import NotificationEvent, NotificationTypesEnum
from text_msg import MSG_TXT

from config import settings as SETT
from db_conn import db_session, init_db
from db_models import Notification

credentials = pika.PlainCredentials(username=SETT.RABBIT_USER, password=SETT.RABBIT_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=SETT.RABBIT_HOST, credentials=credentials))
channel = connection.channel()
channel.queue_bind(exchange=SETT.EXCHANGE, queue=SETT.INSTANT_QUEUE)


def callback(ch, method, properties, body):
    notification = NotificationEvent.parse_raw(body)
    if notification.event_type == NotificationTypesEnum.user_create:
        db_session.add(Notification(notification.user_id, 'user_create',
                                    notification_text=MSG_TXT['user_create'],
                                    user_name=notification.user_name,
                                    user_email=notification.user_email,
                                    ready=True))
        logging.error('BABBIT WORKER user_create')
    elif notification.event_type == NotificationTypesEnum.change_password:
        db_session.add(Notification(notification.user_id, 'change_password',
                                    notification_text=MSG_TXT['change_password'],
                                    user_name=notification.user_name,
                                    user_email=notification.user_email,
                                    ready=True))
        logging.error('BABBIT WORKER change_password')
    elif notification.event_type == NotificationTypesEnum.received_likes:
        db_session.add(Notification(notification.user_id, 'received_likes',
                                    notification_text=MSG_TXT['received_likes'],
                                    user_name=notification.user_name,
                                    user_email=notification.user_email,
                                    ready=False))
        logging.error('BABBIT WORKER received_likes')
    db_session.commit()


init_db()

channel.basic_consume(
    queue=SETT.INSTANT_QUEUE, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
