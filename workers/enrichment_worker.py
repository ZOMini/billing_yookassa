import asyncio
import logging
import time

import aiohttp

from config import settings as SETT
from db_conn import db_session, init_db
from db_models import AdminNotifEvent, Notification, NotificationTypesEnum

init_db()


async def _enrich_user_by_id(n: Notification):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=25, loop=asyncio.get_event_loop())) as client:
            async with client.get(f'{SETT.AUTH_URL}?id={n.user_id}') as resp:
                if resp.status == 200:
                    _json = await resp.json()
                    n.user_email = _json['email']
                    n.user_name = _json['username']
                    n.ready = True
                    db_session.commit()
                else:
                    logging.error('ENRICH FAIL - %s - %s', resp.status, n.id)
                    db_session.rollback()
    except Exception as e:
        logging.error("enrich error - %s", e)


async def enrich_received_likes():
    notifications = db_session.query(Notification).filter(
        Notification.notification_type == "received_likes",
        Notification.status == False,
        Notification.ready == False
    )
    for n in notifications:
        await _enrich_user_by_id(n)


async def enrich_new_film():
    nonif_admin = db_session.query(AdminNotifEvent).filter(
        AdminNotifEvent.notification_type == "new_films",
        AdminNotifEvent.status == False
    )
    for na in nonif_admin:
        for _id in na.user_ids:
            n = Notification(_id,
                             NotificationTypesEnum.new_films,
                             na.notification_text,
                             status=False,
                             ready=False)
            db_session.add(n)
            db_session.commit()
            await _enrich_user_by_id(n)
        na.status = True
        db_session.commit()

while True:
    loop = asyncio.new_event_loop()
    tasks = [enrich_received_likes(),
             enrich_new_film()]

    async def main():
        await asyncio.gather(*tasks)
    loop.run_until_complete(main())
    time.sleep(5)
