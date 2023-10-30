import json
import random
import time

from bson import ObjectId
from bson.errors import BSONError
from flask import request, Blueprint

from .db.mongo import notifications_collection
from .models import NotificationCreate, NotificationList, NotificationRead
from .smtp.smtp import send_email
from .validators import validate_request

endpoints = Blueprint('endpoints', __name__)


@endpoints.route('/create', methods=['POST'])
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


@endpoints.route('/list')
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


@endpoints.route('/read', methods=['POST'])
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
