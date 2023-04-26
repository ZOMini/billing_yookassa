import logging

import requests

from core.config import settings


def notif_send(username: str, email: str, user_id: str):
    param = {'user_id': str(user_id), 'email': email, 'username': username}
    resp = requests.post(
        f'{settings.notif_api_url}/notif/api/v1/create_user', json=param)
    if resp.status_code != 201 or resp.status_code != 200:
        logging.error('ERROR - notif_send() - status %s', resp.status_code)
    else:
        logging.info('INFO - notif_send() - status %s', resp.status_code)
