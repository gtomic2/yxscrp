import sys
import os
sys.path.append(os.getcwd())
from lxml import html
import requests 
import json
import pymongo
import webbrowser
import datetime
from NewItems import Items
conn = pymongo.MongoClient()
db = conn.items_database

with open('tags.json', 'r') as tags:
    tags = json.load(tags)

def timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")

def update_db(ID, field, value,update_type):
        db.items.update({
            'ID': ID
            }, {
                '$set':{ 
                    field: value,
                    'timestamp': timestamp(),
                    'update':update_type
                    }
                }, upsert = False)
        return 

def new_items(site):
    f = open(os.path.join('designers.txt'), 'r')
    brands = f.readlines()
    for brand_url in brands:
        brand, url = brand_url.split(',')
        items = Items(url, site, brand)
        items.create()
    f.close()

def thread_stop(beg, count, end):
    if beg >= 0:
        if count < beg:
            return False
        if count > end:
            return True
    return False

def final_sale():
    site = 'yoox'
    items = db.items.find({'soldout':{'$ne': 1}})
    print ("CHECKING {} ITEMS".format(len(list(items))))
    final_sale_message = 'SALE OF THIS MERCHANDISE IS FINAL. YOOX offers no refunds, credits or exchanges for this item.'
    for i,item in enumerate(items):
        if i % 50 == 0:
            print ("checked {} items".format(i))
        if not item['url']:
            continue
        if 'final-sale' in item:
            continue
        url = get_url(site, item['url'])
        final_sale = query_item(url, tags[site]['final'])
        final = True if final_sale_message in final_sale else False
        update_db(item['ID'], 'final-sale', final, 'final-sale')
        if final:
            print ("final sale item found: {}".format(item['ID']))

#find soldout items that have returned
def returns(site='yoox', end = 0):
    items = db.items.find({'soldout': 1})
    total = items.count()
    search_length = total // 4
    end = end*search_length
    beg = end - search_length
    print("checking {0} sold out items".format(items.count()))
    print("starting at {0} ending at {1}".format(beg, end))
    for count, item in enumerate(items):
        if beg >= 0:
            if count < beg:
                continue
            if count > end:
                break
        if count % 50 == 0:
            print("checked {0} items".format(count))
        url = get_url(site, item['url'])
        prices = item['price']
        db_price = prices[0]
        cur_price = query_item(url, tags[site]['price'])
        if not cur_price:
            continue
        update_db(item["ID"], 'soldout', 0,'return')
        print('soldout item returned: {0}'.format(item["ID"]))
        cur_price = int(cur_price[0].split('$')[1].split('.')[0].replace(",",""))
        if cur_price < db_price:
            percent_off = (db_price-cur_price)/db_price
            print('dropped {0} from {1} to {2} for {3}'.format(percent_off, db_price, cur_price, item['ID']))
            prices.insert(0,cur_price)
            update_db(item["ID"], "price", prices, 'return')
    return


def get_range(q, n):
    if q == 0:
        return 0,n
    start = (q-1)*n//4
    end = q*n//4
    return start, end

# find price drops for items currently in database
def price_drops(brand='all', site='yoox', quartile = 0):
    if brand == "all":
        items = db.items.find({})
    else: 
        items = db.items.find({'brand':brand})
    print("checking {0} items".format(items.count()))
    start, end = get_range(quartile, items.count())
    print(" indexing over ({0} - {1})".format(start,end))
    soldout_items = [item["ID"] for item in  db.items.find({'soldout':1})] 
    count = 0
    for count, item in enumerate(items):
        if count < start:
            continue
        if count > end:
            break
        if count % 100 == 0:
            print("checked {0} items".format(count))
        url = get_url(site, item['url'])
        if not url:
            continue
        if 'timestamp' in item and 'update' in item:
            if item['timestamp'] == timestamp() and item['update'] == 'drop':
                print("skipping checked item")
                continue
        prices = item['price']
        db_price = prices[0]
        cur_price = query_item(url, tags[site]['price'])#'//span[@itemprop="price"]/text()')
        if not cur_price:
            if item['ID'] not in soldout_items:
                update_db(item["ID"], 'soldout', 1,'sold')
            continue

        if item["ID"] in soldout_items:
            update_db(item["ID"], 'soldout', 0,'return')
            print('soldout item returned: {0}'.format(item["ID"]))
            
        cur_price = int(cur_price[0].split('$')[1].split('.')[0].replace(",",""))
        if cur_price < db_price:
            prices.insert(0, cur_price)
            percent_off = round((db_price-cur_price)/db_price, 2)
            print('dropped {0} from {1} to {2} for {3}'.format(percent_off, db_price, cur_price,item['ID']))
            update_db(item["ID"], "price", prices, 'drop')
            update_db(item["ID"],"current_price", cur_price, 'drop')
    return

def query_item(itemurl, query):
    page = requests.get(itemurl)
    tree = html.fromstring(page.content)
    return tree.xpath(query)


def get_url(site, path):
    if not path:
        return 0
    url = 'http://www.{0}.com{1}'.format(site, path)
    return url

# find items tagged with promo discount
def promotions(site='yoox'):
    items = db.items.find({"$or":[ {'soldout': 0}, {'soldout': {'$exists':0}}]})
    print("checking {0} items for promotions".format(items.count()))
    total = items.count()
    for count, item in enumerate(items):
        if count % 50 == 0:
            print("{0} % complete".format(100*round(count/total,3)))
        print(item['url'])
        if not item['url']:
            continue
        promo = query_item(get_url(site, item['url']), tags[site]['promotions'])
        if promo:
            print("promo found {}".format(item['ID']))
            update_db(item['ID'], 'promotion',promo[0],'promo')
           

