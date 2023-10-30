from enum import Enum
from typing import Optional, Annotated

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, field_validator, Field

import config


class Keys(str, Enum):
    registration = 'registration'
    new_message = 'new_message'
    new_post = 'new_post'
    new_login = 'new_login'


class BaseUserModel(BaseModel):
    user_id: str


class NotificationCreate(BaseUserModel):
    key: Keys
    target_id: Optional[str] = None
    data: Optional[dict] = None

    @field_validator('target_id')
    def invalid_id(cls, target_id: str):
        if ObjectId(target_id):
            raise InvalidId(
                f"'{target_id}' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"
            )
        return target_id


class NotificationList(BaseUserModel):
    skip: Annotated[int, Field(ge=0, default=0)]
    limit: Annotated[int, Field(gt=0, default=config.NOTIFICATION_LIMIT)]


class NotificationRead(BaseUserModel):
    notification_id: str
