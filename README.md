# Проектная работа: диплом - тема биллинг

# Для проверки:
  - https://github.com/ZOMini/graduate_work  - репозиторий
  - https://github.com/ZOMini/graduate_work/invitations - приглашение
  - группа 10 - Пирогов Виталий/Игорь Синякин(@ee2 @sinyakinmail - в пачке)

# Запуск
  - docker-compose -f docker-compose-bill.yml -f docker-compose-notif.yml up --build

# Полезности
  - сертификат ssl для HTTPS, браузеры будут ругаться(серты самоподписанные) - игнорим. Файлы создаем в линуксе, кладем в папку ./billing
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