from flask import Flask, render_template
from flask.ext.pymongo import PyMongo
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
from importlib.machinery import SourceFileLoader
import datetime
import sys, os
sys.path.append(os.getcwd())
import check_db

app = Flask(__name__)
Bootstrap(app)
conn = MongoClient()
db = conn.items_database
now = datetime.datetime.now()

@app.route('/new')
def new():
    check_db.new_items('yoox')
    data =  db.items.find({'timestamp':check_db.timestamp(),'update':'new'})
    return render_template('home2.html', data=data)


@app.route('/show_final')
def show_final():
    data = db.items.find({'final-sale':True})
    return render_template('home2.html', data=data)

@app.route('/final')
def final():
    check_db.final_sale()
    data = db.items.find({'update':'final-sale'})
    return render_template('home2.html', data=data)

@app.route('/drops')
def drops():
    check_db.price_drops()
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'drop'})
    return render_template('home2.html',data=data)

@app.route('/drops_1')
def drops_1():
    check_db.price_drops(quartile=1)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'drop'})
    return render_template('home2.html',data=data)

@app.route('/drops_2')
def drops_2():
    check_db.price_drops(quartile=2)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'drop'})
    return render_template('home2.html',data=data)

@app.route('/drops_3')
def drops_3():
    check_db.price_drops(quartile=3)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'drop'})
    return render_template('home2.html',data=data)

@app.route('/drops_4')
def drops_4():
    check_db.price_drops(quartile=4)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'drop'})
    return render_template('home2.html',data=data)



@app.route('/promo')
def promo():
    check_db.promotions('yoox')
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'promo'}).sort('current_price',1)
    return render_template('home2.html',data=data)

@app.route('/show_promo')
def show_promo():
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'promo'}).sort('_id')
    return render_template('home2.html',data=data)


@app.route('/show_drops')
def showDrops():
    data = db.items.find({'timestamp': check_db.timestamp(), 'update':'drop'}).sort('current_price',1)
    return render_template('home2.html',data=data)

@app.route('/returns')
def returns():
    check_db.returns('yoox')
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})
    
    return render_template('home2.html', data=data)

@app.route('/returns_1')
def returns_1():
    check_db.returns('yoox',end=1)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})
   

@app.route('/returns_2')
def returns_2():
    check_db.returns('yoox', end=2)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})
    

@app.route('/returns_3')
def returns_3():
    check_db.returns('yoox', end=3)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})
    


@app.route('/returns_4')
def returns_4():
    check_db.returns('yoox', end=4)
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})



@app.route('/show_returns')
def show_returns():
    data = db.items.find({'timestamp':check_db.timestamp(), 'update':'return'})   
    return render_template('home2.html', data=data)

def main(port_num):
    app.run(host='127.0.0.1', port=port_num)
if __name__ == '__main__':
    #app.run( use_reloader=False)
    import sys
    main(int(sys.argv[1]))
    #app.run(host='127.0.0.1', port=8000)


