
from pymongo import MongoClient()

client = MongoClient()

db = client.items_database

items = db.items
