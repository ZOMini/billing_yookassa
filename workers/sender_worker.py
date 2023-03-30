import logging
import time

from mail_sender import send_mail
from mailhog import Mailhog
from schedule import every, repeat, run_pending
from sqlalchemy import or_

from db_conn import db_session
from db_models import Notification, NotificationTypesEnum

mailhog = Mailhog()

@repeat(every().second)
def instant_notification_job():
    notifications = db_session.query(Notification).filter(or_(
        Notification.notification_type == NotificationTypesEnum.user_create.value,
        Notification.notification_type == NotificationTypesEnum.change_password.value),
        Notification.ready == True,
        Notification.status == False)
    for n in notifications:
        try:
            logging.error("%s %s %s %s", n.user_email, n.user_name, n.notification_text, 'inst send mail')
            send_mail(n.user_email, n.user_name, n.notification_text, template='instant')
            n.status = True
            db_session.commit()
        except Exception as e:
            logging.error("instant_notification_job EXCEPTION %s", e)
            db_session.rollback()


def deferred_notification_job(notif_type: str):
    user_ids = db_session.query(Notification.user_id).filter(
        Notification.notification_type == notif_type,
        Notification.ready == True,
        Notification.status == False).distinct()
    for id in user_ids:
        try:
            notif_user = db_session.query(Notification).filter(
                Notification.user_id == id[0],
                Notification.ready == True,
                Notification.status == False).all()
            for n in notif_user:
                n.status = True
            if notif_type == 'received_likes':
                cnt = len(notif_user)
                msg = f'На ваши ревью поставили {cnt} лайков! Ждем в гости!'
                send_mail(n.user_email, n.user_name, msg, template='instant')
                logging.error("received_likes email - %s - %s - %s - %s", n.user_email, n.user_name, msg, notif_type)
            elif notif_type == 'new_films':
                send_mail(n.user_email, n.user_name, n.notification_text, template='instant')
                logging.error("new_films email - %s - %s - %s - %s", n.user_email, n.user_name, n.notification_text, notif_type)
            db_session.commit()
        except Exception as e:
            logging.error("deferred_notification_job EXCEPTION %s", e)
            db_session.rollback()


# @repeat(every().day.at('10:30'))
@repeat(every(20).seconds)
def received_likes_job():
    deferred_notification_job(NotificationTypesEnum.received_likes.value)


# @repeat(every().day.at('19:30'))
@repeat(every(20).seconds)
def new_film_job():
    deferred_notification_job(NotificationTypesEnum.new_films.value)


while True:
    run_pending()
    time.sleep(1)
