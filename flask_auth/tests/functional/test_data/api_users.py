user_new = {
     "name": "user_new",
     "password": "12345678",
     "password2": "12345678",
     "email": "user_new@mail.ru",
     "role": ""
}

user_new_pwd_mismatch = {
     "name": "user_new_pwd_mismatch",
     "password": "12345678",
     "password2": "87654321",
     "email": "user_new_pwd_mismatch@mail.ru",
     "role": ""
}

user_new_pwd2_missing = {
     "name": "user_new_pwd2_missing",
     "password": "12345678",
     "email": "user_new_pwd2_missing@mail.ru",
     "role": ""
}

user_new_pwd_missing = {
     "name": "user_new_pwd_missing",
     "email": "user_new_pwd_missing@mail.ru",
     "role": ""
}

#необходимо создать пользователя
user_new_existing = {
     "name": "user_new_existing",
     "password": "12345678",
     "password2": "12345678",
     "email": "user_new_existing@mail.ru",
     "role": ""
}
#необходимо создать пользователя
user_change_pwd = {
     "name": "user_change_pwd",
     "pass_old": "12345678",
     "password": "12345678",
     "password2": "12345678",
     "email": "user_change_pwd@mail.ru",
     "role": ""
}

user_change_wrong_pwd = {
     "name": "user_change_pwd_",
     "pass_old": "341241243",
     "password": "423424242",
     "password2": "12345678",
     "email": "user_change_pwd@mail.ru",
     "role": ""
}

user_change_wrong_username = {
     "name": "user_change_wrong_username",
     "pass_old": "12345678",
     "password": "12345678",
     "password2": "12345678",
     "email": "user_change_wrong_username@mail.ru",
     "role": ""
}

user_change_pwd2_missing = {
     "name": "user_new",
     "pass_old": "12345678",
     "password": "12345678",
     "email": "user_change_wrong_username@mail.ru",
     "role": ""
}

#create user
user_login = {
     "name": "user_login",
     "password": "12345678",
     "email": "user_login@mail.ru",
     'token': None,
     "role": ""
}

user_login_wrong_pwd = {
     'name': 'user_login',
     'password': '87654321',
     'email': 'user_login@mail.ru',
     'token': None,
     "role": ""
}

user_login_wrong_user = {
     'name': 'user_login_wrong_user',
     'password': '87654321',
     'email': 'user_login_wrong_user@mail.ru',
     'token': None,
     "role": ""
}

user_good_token = {
     'name': 'user_good_token',
     'password': '12345678',
     'email': 'user1@mail.ru',
     'token': '',
     "role": ""
}

user_no_token = {
     'name': 'user_good_token',
     'password': '12345678',
     'email': 'user1@mail.ru',
     'token': None,
     "role": ""
}

user_bad_token = {
     'name': 'user_bad_token',
     'password': '12345678',
     'email': 'user2@mail.ru',
     'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdC',
     "role": ""
}

user_expired_token = {
     'name': 'user_expired_token',
     'password': '12345678',
     'email': 'user2@mail.ru',
     'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3MzA5MDA2OCwianRpIjoiYjU0YmNjMTYtYmNkNC00MmZmLTk5YzktODQxOTNlYjg1OWE3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImJmOGZhYWY3LWQ1MzUtNGQ1Zi1hYzdhLWI3YjJkMmVlMGUyNSIsIm5iZiI6MTY3MzA5MDA2OCwiZXhwIjoxNjczMDkzNjY4LCJ1YSI6MjkyNTQwMTgzNSwiZW1haWwiOiJiYi03QHlhLnJ1Iiwicm9sZXMiOltdfQ.uSUN8_UyX0m0SqWrJQyGr4jZDN-xhzIrvLtBNqw-ysw',
     "role": ""
}

user_expired_refresh_token = {
     'name': 'user_expired_token',
     'password': '12345678',
     'email': 'user2@mail.ru',
     'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3MzA5MDA2OCwianRpIjoiYjU0YmNjMTYtYmNkNC00MmZmLTk5YzktODQxOTNlYjg1OWE3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImJmOGZhYWY3LWQ1MzUtNGQ1Zi1hYzdhLWI3YjJkMmVlMGUyNSIsIm5iZiI6MTY3MzA5MDA2OCwiZXhwIjoxNjczMDkzNjY4LCJ1YSI6MjkyNTQwMTgzNSwiZW1haWwiOiJiYi03QHlhLnJ1Iiwicm9sZXMiOltdfQ.uSUN8_UyX0m0SqWrJQyGr4jZDN-xhzIrvLtBNqw-ysw',
     "role": ""
}

user_admin = {
     "name": "user_admin",
     "password": "12345678",
     "email": "user_admin@mail.ru",
     "role": "admin"
}

user_logout = {
     "name": "user_logout",
     "password": "12345678",
     "email": "user_logout@mail.ru",
     "role": ""
}


user_logout_wrong_token = {
     "name": "user_logout_wrong_token",
     "password": "12345678",
     "email": "user_logout_wrong_token@mail.ru",
     "role": ""
}


user_refresh = {
     "name": "user_refresh",
     "password": "12345678",
     "email": "user_refresh@mail.ru",
     "role": ""
}

user_new_role = {
     "name": "user_new_role",
     "password": "12345678",
     "email": "user_new_role@mail.ru",
     "role": ""
}

user_delete_role = {
     "name": "user_delete_role",
     "password": "12345678",
     "email": "user_delete_role@mail.ru",
     "role": "admin"
}

