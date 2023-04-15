import enum


class ResponseMsg(enum.Enum):
    BAD_REQUEST_RETRY = 'Возврат не возможен. Возврат уже производился. Можно только 1-н раз.'
    BAD_REQUEST_NO_PAYMENTS = 'Возврат не возможен. У пользователя нет оплаченных подписок.'
    BAD_REQUEST_3_DAYS = 'Возврат не возможен. С момента оплаты прошло больше 3-х дней.'
    NOT_FOUND_RETRY = '- redis_id - уже обработан.'
    NOT_FOUND_NO_TARIFF = 'Нет такого тарифа.'
