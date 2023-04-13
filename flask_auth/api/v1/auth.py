import logging
from http import HTTPStatus as HTTP

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, get_jwt, jwt_required

from flask_auth.services.utils import role_required
from services.models_serv import AuthServ, UserServ
from services.utils import check_user_agent, throttling_user_agent

auth = Blueprint('auth', __name__)


@auth.route('/user_crud', methods=['POST', 'PUT'])
@jwt_required(optional=True)
@throttling_user_agent()
def user_crud():
    """
    ---
    post:
      description: Создает пользователя в базе.(поля email, password). Идентификация происходит по name, обязательное поле. Аутентификация не нужна.
      summary: create_user
      requestBody:
        content:
          application/json:
            schema: CreateUserSchema
      responses:
        201:
          description: User created. Login is email
        400:
          description: password != password2 or length < 8  // Wrong email or password or name
        403:
          description: FORBIDDEN
        422:
          description: UNPROCESSABLE ENTITY
      tags:
        - Auth
    put:
      description: Меняет данные пользователя (пароль/юсернайм/емаил). Аутентификация нужна.
      summary: change_user (need access token)
      security:
        - jwt_key: []
      requestBody:
        content:
          'application/json':
            schema: PutUserSchema
      responses:
        202:
          description: User update
        400:
          description: password != password2 or length < 8  // Wrong email or password or name
        401:
          description: UNAUTHORIZED
        403:
          description: FORBIDDEN
      tags:
        - Auth
    """
    response = UserServ.user_crud()
    return response


@auth.route("/login", methods=["POST"])
@throttling_user_agent()
def login():
    """
    ---
    post:
      summary: Возвращает пару (REFRESH/ACCESS)
      description: Принимает логин(email)/пароль, возвращает пару(REFRESH/ACCESS) токенов. Регистрирует авторизацию.
      requestBody:
        description: Логин и пароль
        content:
          application/json:
            schema: LoginInputSchema
      responses:
        200:
          description: Результат получения (REFRESH/ACCESS)
          content:
            application/json:
              schema: OutputSchema
        400:
          description: Ошибка
          content:
            application/json:
              schema: ErrorSchema
        403:
          description: FORBIDDEN
      tags:
        - Auth
    """
    json = request.get_json()
    if 'email' not in json or 'password' not in json:
        return jsonify("Not email or password"), HTTP.BAD_REQUEST
    user: UserServ = UserServ.query.filter_by(email=json['email']).scalar()
    if not user or not user.check_password(json['password'], json['email']):
        return jsonify("Wrong email or password"), HTTP.UNAUTHORIZED
    access_token, refresh_token = AuthServ.login_refresh_service(user, True)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
@check_user_agent()
def logout():
    """
    ---
    delete:
      summary: Logout (need access/refresh token)
      description: Принимает любой действующий токен(ACCESS/REFRESH) и отзывает все(ACCESS/REFRESH) ключи - помещаяя их в redis blocklist.
      responses:
        200:
          description: Access/Refresh tokens revoked
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    AuthServ.logout_service(get_current_user())
    return jsonify('All tokens revoked'), HTTP.OK


@auth.route("/logout_all", methods=["DELETE"])
@jwt_required(verify_type=False)
@check_user_agent()
def logout_all():
    """
    ---
    delete:
      summary: Logout all (need access/refresh token)
      description: Принимает любой действующий токен(ACCESS/REFRESH) и отзывает все(ACCESS/REFRESH) ключи, у всех user_agent's - помещаяя их в redis blocklist..
      responses:
        200:
          description: All Access/Refresh tokens revoked
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    AuthServ.logout_all_service(get_current_user())
    return jsonify('All tokens revoked'), HTTP.OK


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@check_user_agent()
def refresh():
    """
    ---
    post:
      summary: Обновляет пару (REFRESH/ACCESS) (need access/refresh token)
      responses:
        200:
          description: Результат получения обновленного (REFRESH/ACCESS)
          content:
            application/json:
              schema: OutputSchema
        401:
          description: Ошибка
          content:
            application/json:
              schema: ErrorSchema
        401:
          description: Просроченный токен аторизации (REFRESH)
          content:
            application/json:
              schema: ErrorSchema
        422:
          description: Невалидный заголовок авторизации (REFRESH)
          content:
            application/json:
              schema: ErrorSchema
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    user = get_current_user()
    access_token, refresh_token = AuthServ.login_refresh_service(user)
    return jsonify(access_token=access_token, refresh_token=refresh_token), HTTP.CREATED


@auth.route("/history_auth", methods=["GET"])
@jwt_required()
@throttling_user_agent()
def history_auth():
    """
    ---
    get:
      summary: History_auth (need access token)
      description: Возвращает список всех авторизаций пользователя. Необходим Access token.
      parameters:
        - name: page
          in: query
          description: Номер страницы
          required: false
          schema:
            type: integer
        - name: size
          in: query
          description: Размер страницы
          required: false
          schema:
            type: integer
      responses:
        200:
          description: История авторизаций.
          content:
            application/json:
              schema: HistoryAuthSchema
        401:
          description: UNAUTHORIZED
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    jwt_dict = get_jwt()
    page = int(request.args.get('page', default=0))
    size = int(request.args.get('size', default=5))
    history = AuthServ.history_auth(jwt_dict['sub'], page, size)
    return jsonify(history_auth=history)


@auth.route("/check_user", methods=["GET"])
@jwt_required()
def check_user():
    """
    ---
    get:
      summary: check_user (need access token)
      description: Ручка для микросервисов, проверяет валидность access ключа. Необходим Access token.
      responses:
        200:
          description: OK
        401:
          description: UNAUTHORIZED
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    logging.error('INFO USER_AGENT_PLATFORM - %s', request.user_agent)
    return jsonify(), HTTP.OK


@auth.route("/check_user_is_subscriber", methods=["GET"])
@jwt_required()
@role_required('subscriber')
def check_user_is_subscriber():
    """
    ---
    get:
      summary: check_user (need access token)
      description: Ручка для микросервисов, проверяет валидность access ключа и является ли владелец подписчиком. Необходим Access token.
      responses:
        200:
          description: OK.
        401:
          description: UNAUTHORIZED
        403:
          description: FORBIDDEN
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    return jsonify(), HTTP.OK


@auth.route("/get_user_by_id", methods=["GET"])
def get_user_by_id():
    """
    ---
    get:
      summary: get_user
      description: Ручка для микросервисов.
      parameters:
        - name: id
          in: query
          description: ID пользователя
          required: true
          schema:
            type: string
      responses:
        200:
          description: OK.
          content:
            application/json:
              schema: GetByIDUserSchema
        404:
          description: NOT_FOUND
      tags:
        - Auth
    """
    id = request.args.get('id')
    user = UserServ.get_obj_by_id(id)
    if not user:
        return jsonify(), HTTP.NOT_FOUND
    return jsonify(user_id=user.id, username=user.name, email=user.email), HTTP.OK

@auth.route("/get_user_by_name", methods=["GET"])
def get_user_by_name():
    """
    ---
    get:
      summary: get_user_id
      description: Ручка для микросервисов.
      parameters:
        - name: username
          in: query
          description: username пользователя
          required: true
          schema:
            type: string
      responses:
        200:
          description: OK.
          content:
            application/json:
              schema: GetByIDUserSchema
        404:
          description: NOT_FOUND
      tags:
        - Auth
    """
    username = request.args.get('username')
    user = UserServ.get_obj_by_name(username)
    if not user:
        return jsonify(), HTTP.NOT_FOUND
    return jsonify(user_id=user.id), HTTP.OK
