from flask import request

from core.config import jwt
from db.redis import jwt_redis_blocklist
from models.db_models import User
from services.utils import user_agent_hash


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@jwt.additional_claims_loader
def add_claims_to_access_token(identity: User) -> dict:
    ua = user_agent_hash(request.headers.get('User-Agent', 'empty'))
    roles = [role.role for role in identity.role]
    return {
        'ua': ua,
        'email': identity.email,
        'roles': roles,
    }


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None
