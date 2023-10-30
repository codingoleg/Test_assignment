import json
from functools import wraps

from bson import ObjectId
from flask import request
from pydantic import ValidationError

from .db.mongo import user_collection
from .models import BaseUserModel


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
