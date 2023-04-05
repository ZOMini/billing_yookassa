from models.models_pg import PaymentPG


class AioRequests:
    @staticmethod
    def post_headers(idempotency_key):
        headers = {
            'Idempotence-Key': str(idempotency_key),
            'Content-Type': 'application/json',
        }
        return headers


    @staticmethod
    def post_body(amount, user_id, tarif_id, redis_id):
        body = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "metadata": {
                'user_id': str(user_id),
                'tarif_id': str(tarif_id)
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                'enforce': True,
                "return_url": f"https://localhost/yookassa/api/v1/buy_return/{redis_id}"
            },
            "capture": True,
            "description": "Покупка подписки на 30 дней."
        }
        return body


    @staticmethod
    def refund_body(payment: PaymentPG, summ: int):
        body = {
            "amount": {
                "value": f"{summ}",
                "currency": "RUB"
                },
            "payment_id": str(payment.id)
        }
        return body
