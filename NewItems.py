from lxml import html
import requests 
import pymongo
import sys
import json
import webbrowser
import datetime

class Items():
    def __init__(self, url, domain, brand):
        self.db = pymongo.MongoClient().items_database
        self.tags = self.get_xpath_tags(domain)
        self.url = url
        self.tree = self.get_markup(url.format(1))
        self.brand = brand
        self.now = datetime.datetime.now()
        self.time = datetime.datetime.now().strftime("%Y-%m-%d")
        print("getting items from brand {0}".format(brand))

    def get_xpath_tags(self, site):
        with open('tags.json', 'r') as json_data:
            tags = json.load(json_data)
            return tags[site]
 
    def get_markup(self, url):
        page = requests.get(url)
        tree = html.fromstring(page.text)
        return tree
        
    def create(self):
        page_num = 1
        item_urls = self.get_item_urls_from_tree()    
        while item_urls:
            db_items = self.get_db_items("brand", self.brand)   
            new_items, old_items = self.partition_items(db_items)
            print("found {0} new items for {1}".format(len(new_items), self.brand))
            self.add_new_items(new_items)
            page_num += 1
            self.tree = self.get_markup(self.url.format(page_num))
            item_urls = self.get_item_urls_from_tree()

    def get_db_items(self, key,val):
        items = self.db.items.find({key:val})
        item_urls = [item['url'] for item in items]
        item_ids = [self.get_item_id(item) for item in item_urls]
        return item_ids

    def get_item_id(self, url):
        return url.split('/')[2]

    def get_item_urls_from_tree(self):
        return self.tree.xpath(self.tags['id'])

    def partition_items(self, db_items):
        items_in_page = self.tree.xpath(self.tags['id'])
        new_items = set(items_in_page).difference(set(db_items))
        old_items = set(items_in_page).intersection(set(db_items))
        return new_items, old_items

    def get_attribute(self, item_id,attr):
        item_id = "item_" + item_id
        val =  self.tree.xpath(attr.format(item_id))       
        if val == []:
            return False
        return val[0].strip()

    def add_new_items(self, new_items):
        for item_id in new_items:
            if self.sold(item_id):
                continue
            ID = item_id
            price = [self.get_attribute(ID, self.tags['sale_price'])]
            if price:
                price = [int(price[0].split("$")[1].split(".")[0].replace(",",""))]
            url = self.get_attribute(ID, self.tags['url'])
            brand = self.get_attribute(ID, self.tags['brand'])
            cat = self.get_attribute(ID, self.tags['category'])
            img = self.get_attribute(ID, self.tags['img'])
            self.db.items.insert({
                'ID':ID,
                'price':price,
                'current_price':price[0], 
                'url':url,
                'brand':brand, 
                'category':cat, 
                'img': img, 
                "timestamp": self.time,
                'update':'new'
            })

    def sold(self,ID):
        item_available = self.get_attribute(ID,self.tags['sale_price'])
        if not item_available:
            print("soldout item: {0}".format(ID))
            self.db.items.update({'ID':ID},
                {'$set':{
                    'soldout':'1' }}, upsert=False)
            return True
        return False

    def check_promo(self, item):
        promo = self.get_attribute(item, self.tags['promo'],1)
        print("item {0} has promo {0}".format(item, promo))



if __name__ == "__main__":
    import os
    f = open(os.path.join('designers.txt'), 'r')
    brands = f.readlines()
    for brand in brands:
        if "MASNADA" in brand:
            brand, url = brand.split(',')
            items = Items(url, 'yoox', brand)
            items.create()


