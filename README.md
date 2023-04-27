# BILLING - Yookassa

## Описание
  - Дипломный проект по теме "Биллинг".
  - Процессинг выбран yookassa.
  - Для полноценной работы совмещен с ранее написанными сервисами [нотификации](https://github.com/ZOMini/notifications_sprint_1) и [авторизации](https://github.com/ZOMini/Auth_sprint_2).
  - Сервис позволяет принимать оплату, делать возврат ранее внесенных денежных средств.
  - Воркер отслеживает статусы платежей и выдает через сервис авторизации роль подписчика.
  - Он же отзывает роль подписчика если время оплаты закончилось.
  - Так же воркер отправляет увидомления через сервис нотификации:
    - Если произошла удачная оплата.
    - Если осталось менее суток подписки.
    - Если подписка закончилась.
    - Если произошел удачный возврат средств.

## Стек
  FastAPI, aiohttp, SQLAlchemy, Django, Pytest, gunicorn, nginx, alembic, aioredis, Postgres, RabbitMQ, Mailhog

## Архитектура
  https://github.com/ZOMini/billing_yookassa/blob/main/as_is.png

## Запуск
  - docker-compose -f docker-compose-prod.yml up --build
  - docker-compose -f docker-compose-dev.yml up --build
  - для запуска нужны сертификаты для HTTPS(см. полезности)
  - заполняем .env (см. .env.template)
  - тесты теперь автоматом в docker-compose(billing_test)

## URL
  - http://localhost/auth/docs/v1/ - документация модуля Auth
  - https://localhost/yookassa/api/openapi - документация модуля Billing
  - http://localhost/bill/admin - Админка billing
  - http://localhost/notif/admin - Админка notif
  - http://localhost:8025/ - Mailhog
  - http://127.0.0.1:15672/ - RabbitMQ
 
## Миграции(init везде автоматом)
  - доп. миграции, если необходимо то, из папки billing:
    - alembic revision -m "migration2" --autogenerate
    - alembic upgrade head

## Полезности
  - сертификат ssl для HTTPS, браузеры будут ругаться(серты самоподписанные) - игнорим. Файлы создаем в линуксе, кладем в папку ./billing, для prod еще их кладем в ./nginx/pem (это для nginx)
    - openssl req -x509 -nodes -days 3650 -newkey ec:<(openssl ecparam -name prime256v1) -keyout private_key.pem -out certificate.pem
    - gunicorn your-project.wsgi --keyfile private_key.pem --certfile certificate.pem
    - https://stackoverflow.com/questions/67110868/gunicorn-https-certificate-and-keys
  - пример uuid: ffe0d805-3595-4cc2-a892-f2bedbec4ac6
  - смотрим billing_db в шеле контейнера:
    - psql -U app -h localhost -d billing_db
    - SELECT * FROM tarif;
    - SELECT * FROM userstatus;
    - SELECT * FROM payment;
    - SELECT * FROM payment JOIN tarif ON payment.tarif_id=tarif.id;
    - SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE';
  - auth_db:
    - psql -U app -h localhost -d auth_db
    - SELECT * FROM users;
    - SELECT * FROM roles;
  - notif_db:
    - psql -U app -h localhost -d notif_db
    - SELECT * FROM notifications;
    - SELECT * FROM adminnotifevent;
  - redis:
    - redis-cli
    - keys *
  - Примеры запросов billing(нужен актуальный user_id из модуля Auth):
    - https://localhost/yookassa/api/v1/buy_subscription?user_id=7d47c389-89ca-435f-8a78-f50734810fc8&tarif_id=ffe0d805-3595-4cc2-a892-f2bedbec4ac1
    - https://localhost/yookassa/api/v1/refunds_subscription/7d47c389-89ca-435f-8a78-f50734810fc8

## Для проверки:
  - https://github.com/ZOMini/graduate_work  - репозиторий
  - https://github.com/ZOMini/graduate_work/invitations - приглашение
  - группа 10 - Пирогов Виталий/Игорь Синякин(@ee2 @sinyakinmail - в пачке)