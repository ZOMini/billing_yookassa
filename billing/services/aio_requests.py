from models.models_pg import PaymentPG, Tariff


class AioRequests:
    @staticmethod
    def post_headers(idempotency_key):
        headers = {
            'Idempotence-Key': str(idempotency_key),
            'Content-Type': 'application/json',
        }
        return headers

    @staticmethod
    def post_body(user_id: str, tarif: Tariff, redis_id: str):
        body = {
            "amount": {
                "value": tarif.price,
                "currency": "RUB"
            },
            "metadata": {
                'user_id': str(user_id),
                'tarif_id': str(tarif.id)
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
            "description": tarif.description
        }
        return body

    @staticmethod
    def refund_body(payment: PaymentPG):
        body = {
            "amount": {
                "value": f"{payment.income}",
                "currency": "RUB"
            },
            "payment_id": str(payment.id)
        }
        return body
