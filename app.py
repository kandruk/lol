import json
import sqlite3
#niepotrzebnie tyle dodałem
from flask import Flask, g, render_template, request, jsonify, redirect, url_for
import itertools

DATABASE = 'sakila.db'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def hello():
    return("hello")

@app.route('/cities', methods=['GET'])
def cities_by_country():
    db = get_db()
    cursor = db.cursor()
    if 'country_name' in request.args:
        country_name= str(request.args['country_name'])
        country_id = (cursor.execute('SELECT country_id FROM country WHERE country = :country_name',{'country_name': country_name}).fetchone())
        id_miasta = int(country_id[0])
        data = cursor.execute('SELECT city FROM city WHERE country_id=:country_id',{'country_id': id_miasta}).fetchall()
        cursor.close()
        return jsonify(data)
    if 'per_page' in request.args and 'page' in request.args:
        per_page= str(request.args['per_page'])
        page = str(request.args['page'])
        a = int(per_page)
        b = int(page)
        c = int((b*a)-a)
        data = cursor.execute('SELECT city FROM city LIMIT:a OFFSET:b',{'a': a, 'b' : c}).fetchall()
        cursor.close()
        return jsonify(data)
    if request.args.get('format') == 'json':
        data = cursor.execute('SELECT city FROM city').fetchall()
        cursor.close()
        return jsonify(data)

@app.route('/cities',methods=['POST'])
def cities_add():
    db = get_db()
    numerek = db.execute('SELECT city_id FROM city ORDER BY city_id DESC LIMIT 1').fetchone()
    country_id = request.get_json('country_id')
    city = request.get_json('city_name')
    city_id = (numerek[0]+1)
    last_update = "2018-01-29 09:58:17"
    db.executescript(
        'INSERT INTO city (country_id, city, city_id, last_update) VALUES ("{}", "{}", "{}", "{}")'
        .format(country_id, city, city_id, last_update)
    )
    db.commit()
    data = db.execute(
        'SELECT country_id, city, city_id FROM city WHERE city_id = :city_id',
        {'city_id': city_id}).fetchone()
    return jsonify(data)

@app.route('/lang_roles')
def lang_list():
    query = '''
    SELECT name, COUNT(*) from language
    join film using (language_id)
    JOIN film_actor using (film_id) 
    GROUP by name
    '''
    args = ()
    db = get_db()
    data = db.execute(query, args).fetchall()
    return_json= []
    for i in data:
        return_json.extend(list(i))
        return_json = dict(itertools.zip_longest(*[iter(return_json)] * 2, fillvalue=""))

    return jsonify(return_json)
