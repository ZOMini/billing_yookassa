import logging
import os

import django
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv('config/.env')

username = os.environ.get('supername', 'superuser')
email = os.environ.get('email', 'user@example.com')
password = os.environ.get('superpass', 'password')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_notif.settings')  # !!!
django.setup()
application = get_wsgi_application()

from django.contrib.auth.models import User

logging.basicConfig(format='%(asctime)s[%(name)s]: %(message)s', level='DEBUG')
logger = logging.getLogger(__name__)

users = User.objects.all()
if not users:
    User.objects.create_superuser(username=username,
                                  email=email,
                                  password=password,
                                  is_active=True,
                                  is_staff=True)
    logger.error('\nSuperuser created! username = %s password = %s',
                   username, password)
else:
    logger.error('\nSuperuser not created, there are already users.')
