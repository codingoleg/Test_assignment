import json
import random
import time
from enum import Enum
from functools import wraps
from typing import Optional, Annotated

from bson import ObjectId
from bson.errors import InvalidId, BSONError
from flask import Flask, request
from pydantic import BaseModel, ValidationError, field_validator, Field

import config
from db.mongo import user_collection, notifications_collection
from smtp.smtp import send_email

app = Flask(__name__)
app_client = app.test_client()


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


def validate_request(model: BaseUserModel):
    """Decorator for either body or args to validate, but neither both. Checks user existence."""

    def decorator(f):
        @wraps(f)
        def wrapper():
            try:
                request_data = json.loads(request.data)
            except json.decoder.JSONDecodeError:
                request_data = dict(request.args.items())
                if not request_data:
                    return {"error": f"args or body were not found"}, 400

            try:
                data = model.model_validate(request_data)
            except ValidationError as error:
                return error.json(), 400

            if not user_collection.find_one({'_id': ObjectId(data.user_id)}):
                return {"error": f"'user_id': '{data.user_id}' was not found"}, 400

            return f()

        return wrapper

    return decorator


@app.route('/create', methods=['POST'])
@validate_request(NotificationCreate)
def create() -> tuple[dict, int]:
    """
    Sends an email or creates a record in the db or both depending on request 'key' value.
    Returns:
        A successful result or an unsuccessful result with an error message.
    """
    response = {}
    doc = {
        **json.loads(request.data),
        'notification_id': str(random.randint(0, 1)),
        'timestamp': int(time.time()),
        'is_new': True
    }

    if doc['key'] in ('registration', 'new_login'):
        sent, email_error = send_email(doc['key'])
        if sent:
            response['email'] = True
        else:
            response['email'] = False
            response["email_error"] = email_error

    if doc['key'] in ('new_message', 'new_post', 'new_login'):
        try:
            result = notifications_collection.insert_one(doc)

            # Update 'target_id' field value of just inserted document
            target_id = doc['target_id'] if doc.get('target_id') else str(result.inserted_id)
            notifications_collection.update_one(
                {"_id": ObjectId(result.inserted_id)}, {'$set': {'target_id': target_id}}
            )
        except BSONError:
            response['db'] = False
        else:
            response['db'] = True

    status_code = 201 if all(response.values()) else 400

    return response, status_code


@app.route('/list')
@validate_request(NotificationList)
def get_list() -> dict:
    """
    Gets number of all records, number of unread records and content of all records.
    Returns:
        Dict with the data above and the request body.
    """
    body = json.loads(request.data)

    elements = notifications_collection.count_documents(
        {'user_id': body['user_id']}, skip=body['skip'], limit=body['limit']
    )
    new = notifications_collection.count_documents({'user_id': body['user_id'], 'is_new': True})
    notifications_list = [
        doc for doc in notifications_collection.find(
            {'user_id': body['user_id']}, skip=body['skip'], limit=body['limit'], projection={'_id': False}
        )
    ]

    return {
        'success': True,
        'data': {
            'elements': elements,
            'new': new,
            'request': {
                'user_id': body['user_id'],
                'skip': body['skip'],
                'limit': body['limit'],
            },
        },
        'list': notifications_list
    }


@app.route('/read', methods=['POST'])
@validate_request(NotificationRead)
def read() -> tuple[dict, int]:
    """
    Finds records with specified user_id and notification_id. If found updates 'is_new' field to False.
    Returns:
        A successful result if at least one record was modified or an unsuccessful result.
    """
    args = dict(request.args.items())

    result = notifications_collection.update_many(
        {"user_id": args['user_id'], 'notification_id': args['notification_id']}, {'$set': {'is_new': False}}
    )

    return ({"success": True}, 200) if result.modified_count else ({"success": False}, 400)


if __name__ == '__main__':
    app.run(host=config.HOST, port=int(config.PORT), debug=True)
