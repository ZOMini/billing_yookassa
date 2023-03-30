import orjson
from pydantic import UUID4, BaseModel

from db_models import NotificationTypesEnum


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrJsonModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class NotificationEvent(OrJsonModel):
    user_id: UUID4
    event_type: NotificationTypesEnum
    user_name: str | None = None
    user_email: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": "dadd35b1-7b11-4aa1-a871-61fddb4faa27",
                "event_type": "user_create",
                "user_name": "username",
                "user_email": "email"
                # "datetime": "2023-03-13 21:12:30.511956"
            }
        }
