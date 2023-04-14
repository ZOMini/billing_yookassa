import os
import runpy
import sys
import time

from dotenv import load_dotenv

load_dotenv()

time.sleep(2)  # Ждем на всякий.
# Фейк миграция movies, так как типо ставим на готовую базу.

# Миграции Django.
sys.argv = ['', 'makemigrations']
runpy.run_path('./manage.py', run_name='__main__')

sys.argv = ['', 'migrate', 'billing', '--fake']
runpy.run_path('./manage.py', run_name='__main__')

sys.argv = ['', 'migrate']
runpy.run_path('./manage.py', run_name='__main__')

# Собираем статику.
sys.argv = ['', 'collectstatic', '--noinput']
runpy.run_path('./manage.py', run_name='__main__')

# Создаем суперпользователя(superuser/password).
username = os.environ.get('supername', 'superuser')
email = os.environ.get('email', 'user@example.com')
password = os.environ.get('superpass', 'password')
sys.argv = ['', 'create_superuser2', '--username', username, '--password', password, '--noinput', '--email', email, '--preserve']
runpy.run_path('./manage.py', run_name='__main__')
