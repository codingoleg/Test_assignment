import os

# Flask
HOST = os.environ['HOST']
PORT = os.environ['PORT']

# MongoDB
NOTIFICATION_LIMIT = 5
TEST_USER_ID = '653ac2ebd8ee28ba0ff7d744'
DB_URI = os.environ['DB_URI']
DB_NAME = os.environ['DB_NAME']

# SMTP
EMAIL = os.environ['EMAIL']
SMTP_HOST = os.environ['SMTP_HOST']
SMTP_PORT = os.environ['SMTP_PORT']
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
SMTP_EMAIL = os.environ['SMTP_EMAIL']
SMTP_NAME = os.environ['SMTP_NAME']
