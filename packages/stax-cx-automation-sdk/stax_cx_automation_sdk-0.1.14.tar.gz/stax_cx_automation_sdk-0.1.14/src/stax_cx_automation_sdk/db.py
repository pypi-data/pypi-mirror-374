from pymongo import MongoClient
from os import getenv

db = MongoClient(getenv('DB_URI')).get_database(getenv('DB_NAME', default='db'))