from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.mongodb_uri)
db = client[settings.db_name]