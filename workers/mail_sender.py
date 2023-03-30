import os
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader, Template

from config import settings as SETT


def send_mail(to: str, name: str, data: str, template: str):
    with smtplib.SMTP(SETT.SMTP_HOST, int(SETT.SMTP_PORT)) as server:
        server.login(user=SETT.SMTP_USER, password=SETT.SMTP_PASSWORD)
        message = EmailMessage()
        message["From"] = SETT.SMTP_USER
        message["To"] = to
        message["Subject"] = 'Уведомление :)'
        env = Environment(loader=FileSystemLoader(f'{os.path.dirname(__file__)}'))
        _template = env.get_template(f'{template}.html')
        output = _template.render(**{
            'title': f'Привет, {name}!',
            'text': f'{data}',
        })
        message.add_alternative(output, subtype='html')
        server.sendmail(from_addr=SETT.SMTP_USER, to_addrs=to, msg=message.as_string())
        server.close()
