import datetime

DEBUG = True

CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
CORS_ORIGINS = ['http://localhost', 'http://localhost:63342']

JWT_EXPIRATION_DELTA = datetime.timedelta(hours=2)
