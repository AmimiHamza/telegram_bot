import os

def get_db_url(ENV):
    if ENV == 'DEV':
        DB_URL = os.getenv("DATABASE_URL_DEV")
    else:
        DB_URL = os.getenv("DATABASE_URL_PROD")
    return DB_URL

