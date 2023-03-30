from marshmallow import Schema, fields


class LoginInputSchema(Schema):
    email = fields.Email(description="Email", load_default='ee-12@ya.ru')
    password = fields.Str(description="Password", load_default='superpass')


class OutputSchema(Schema):
    access_token = fields.Str(description="access_token", required=True)
    refresh_token = fields.Str(description="refresh_token", required=True)


class ErrorSchema(Schema):
    error = fields.Str(description="error", required=True)


class CreateUserSchema(Schema):
    name = fields.Str(description="Name", load_default='admin2')
    email = fields.Email(description="Email", load_default='ee-12@ya.ru')
    password = fields.Str(description="Password", load_default='superpass')
    password2 = fields.Str(description="Password", load_default='superpass')


class PutUserSchema(CreateUserSchema):
    pass_old = fields.Str(description="Old_password", load_default='superpass')


class HistoryAuthSchema(Schema):
    history_auth = fields.List(fields.Str(), load_default=['2023-01-02T19:06:58.824751', 'vsc -- 1 --'])


class RoleSchema(Schema):
    role = fields.Str(description='Role', load_default='admin')


class UserRoleSchema(RoleSchema):
    user = fields.Str(description='User', load_default='admin2')


class UserSchema(Schema):
    user = fields.Str(description='User', load_default='admin2')


class PutRoleSchema(Schema):
    old_role = fields.Str(description='Old Role', load_default='admin')
    new_role = fields.Str(description='New Role', load_default='admin')


class ListRolesSchema(Schema):
    roles = fields.List(fields.Str(description='List All Roles', load_default='admin'))

class GetByIDUserSchema(Schema):
    name = fields.Str(description="Name", load_default='admin2')
    email = fields.Email(description="Email", load_default='ee-12@ya.ru')
    user_id = fields.Str(description="User id", load_default='253d8eb7-9b38-465a-976b-0972c1ba0fa1')
