import pymongo
import sys
conn = pymongo.MongoClient()
db = conn.items_database


items = db.items.find({})

for item in items:
    prices = item['price']
    int_price = []
    prices = [int(price) for price in prices]
    print(prices)
    db.items.update({
        "ID":item['ID']
        },{
            '$set': {
                "price":prices
                }
            }, upsert = False)

