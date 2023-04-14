import uuid

user_create_data = {
    "email": "ea-52@ya.ru",
    "name": "admin52",
    "password": "superpass",
    "password2": "superpass"}

payment_for_subscription = {
    "id": uuid.uuid4(),
    "payment": "card_type - **** **** **** 9999",
    "income": 100,
    "status": "succeeded"}
