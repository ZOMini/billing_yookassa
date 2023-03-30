from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from flask_auth.services.models_serv import RoleServ, UserServ
from flask_auth.services.utils import role_required

role = Blueprint('role', __name__)


@role.route('/role_crud', methods=['GET', 'POST', 'DELETE', 'PUT'])
@jwt_required()
@role_required('admin')
def role_crud():
    """
    ---
    post:
      summary: Create role (need access token)
      description: Создает роль. Аутентификация нужна.
      security:
        - jwt_key: []
      requestBody:
        content:
          application/json:
            schema: RoleSchema
      responses:
        201:
          description: Role created
        403:
          description: FORBIDDEN
        422:
         description: UNPROCESSABLE ENTITY
      tags:
        - Role
    put:
      summary: Change role (need access token)
      description: Обновлят роль. Аутентификация нужна.
      security:
        - jwt_key: []
      requestBody:
        content:
          'application/json':
            schema: PutRoleSchema
      responses:
        202:
          description: Role update
        403:
          description: FORBIDDEN
        422:
         description: UNPROCESSABLE ENTITY
      tags:
        - Role
    delete:
      summary: Delete role (need access token)
      description: Удаляет роль. Аутентификация нужна.
      security:
        - jwt_key: []
      requestBody:
        content:
          'application/json':
            schema: RoleSchema
      responses:
        204:
          description: Role delete
        403:
          description: FORBIDDEN
        422:
         description: UNPROCESSABLE ENTITY
      tags:
        - Role
    get:
      summary: List roles (need access token)
      description: Отдает лист всех ролей. Аутентификация нужна.
      security:
        - jwt_key: []
      responses:
        204:
          description: List roles
          content:
            application/json:
              schema: ListRolesSchema
        403:
          description: FORBIDDEN
        422:
          description: UNPROCESSABLE ENTITY
      tags:
        - Role
    """
    response = RoleServ.role_crud()
    return response


@role.route('/user/roles', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_role_for_user():
    """
    ---
    post:
     summary: Add role for user (need access token)
     description: Добавляет роль пользователю. Аутентификация нужна.
     security:
       - jwt_key: []
     requestBody:
       content:
         application/json:
           schema: UserRoleSchema
     responses:
       201:
         description: Added role for user
       400:
         description: BAD REQUEST.
       422:
         description: UNPROCESSABLE ENTITY
     tags:
       - Role
    """
    json = request.get_json()
    response = UserServ.add_or_del_role_user(json, True)
    return response


@role.route('/user/roles', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_role_from_user():
    """
    ---
    delete:
        summary: Delete role from user (need access token)
        description: Удалает роль (отзывает все ключи). Аутентификация нужна.
        security:
          - jwt_key: []
        requestBody:
            content:
                application/json:
                  schema: UserRoleSchema
        responses:
          200:
            description: Role delete from user.
          400:
            description: BAD REQUEST.
          422:
            description: UNPROCESSABLE ENTITY
        tags:
          - Role
    """
    json = request.get_json()
    response = UserServ.add_or_del_role_user(json)
    return response


@role.route('/user/roles/<string:user>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user_roles(user: str):
    """
    ---
    get:
        summary: Get user roles (need access token)
        description: Удаляет роль пользователя. Аутентификация нужна.
        security:
          - jwt_key: []
        parameters:
        - name: user
          in: path
          description: user
          schema:
            type: string
        responses:
          200:
            description: Role delete.
            content:
                application/json:
                    schema: ListRolesSchema
          404:
            description: No Role // No User
          422:
            description: UNPROCESSABLE ENTITY
        tags:
          - Role
    """
    response = UserServ.get_user_roles(user)
    return response


@role.route('/user/roles/billing', methods=['POST', 'DELETE'])
@jwt_required()
@role_required('admin')
def add_role_for_user_billing():
    """
    ---
    post:
      summary: Add role for user (need access token)
      description: Добавляет роль пользователю. Аутентификация нужна.
      security:
        - jwt_key: []
      requestBody:
        content:
          application/json:
            schema: UserRoleSchema
      responses:
        201:
          description: Added role for user
        400:
          description: BAD REQUEST.
        422:
          description: UNPROCESSABLE ENTITY
      tags:
        - Role
    delete:
      summary: Delete role from user (need access token)
      description: Удалает роль (отзывает все ключи). Аутентификация нужна.
      security:
        - jwt_key: []
      requestBody:
          content:
              application/json:
                schema: UserRoleSchema
      responses:
        200:
          description: Role delete from user.
        400:
          description: BAD REQUEST.
        422:
          description: UNPROCESSABLE ENTITY
      tags:
        - Role
    """
    add = True if request.method == 'POST' else False
    json = request.get_json()
    
    response = UserServ.add_or_del_role_user_billing(json, add)
    return response
