class AioRequests:
    @staticmethod
    def post_headers(idempotency_key):
        headers = {
            'Idempotence-Key': str(idempotency_key),
            'Content-Type': 'application/json',
        }
        return headers

    @staticmethod
    def post_body(user_id, redis_id):
        body = {
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "metadata": {
                'user_id': str(user_id)
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://localhost/yookassa/api/v1/buy_return/{redis_id}"
            },
            "capture": True,
            "description": "Покупка подписки на 30 дней."
        }
        return body
