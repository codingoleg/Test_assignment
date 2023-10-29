import pymongo
from bson import ObjectId

import config

USER_COLLECTION_NAME = 'user_' + config.TEST_USER_ID
NOTIFICATIONS_COLLECTION_NAME = 'notifications_' + config.TEST_USER_ID
MAX_COLLECTION_SIZE = 1125899906842624  # 1 Petabyte

db_client = pymongo.MongoClient(config.DB_URI)
db = db_client[config.DB_NAME]

db.drop_collection(USER_COLLECTION_NAME)
db.drop_collection(NOTIFICATIONS_COLLECTION_NAME)

user_collection = db[USER_COLLECTION_NAME]
notifications_collection = db.create_collection(
    NOTIFICATIONS_COLLECTION_NAME, capped=True, max=config.NOTIFICATION_LIMIT, size=MAX_COLLECTION_SIZE
)

# Add test user to the user_collection
user_collection.insert_one({"_id": ObjectId(config.TEST_USER_ID), "email": config.EMAIL})
