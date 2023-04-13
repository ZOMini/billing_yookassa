import datetime

user_create_data = {
    "email": "test@ya.ru",
    "name": "testuser",
    "password": "testpass",
    "password2": "testpass"}
tariff_id = 'ffe0d805-3595-4cc2-a892-f2bedbec4ac1'

tariff_dict = dict(id='ffe0d805-3595-4cc2-a892-f2bedbec4ac1',
                   days=datetime.timedelta(30),
                   price=100.0,
                   description='Покупка подписки на 30 дней.')
