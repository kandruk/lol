import json
import sqlite3
from flask import Flask, g, render_template, request, jsonify, redirect, url_for

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
def powitalna():
	return("testujemy")

@app.route('/cities')
def miasta():
    db = get_db()
    cursor = db.cursor()
    data = cursor.execute('SELECT city FROM city').fetchall()
    cursor.close()
    return jsonify(data)

@app.route('/cities<country_name>', methods=['GET'])
def grupa(country_name):
    db = get_db()
    cursor = db.cursor()
    country_id = (cursor.execute('SELECT country_id FROM country WHERE country = :country_name',{'country_name': country_name}).fetchone())
    id_miasta = int(country_id[0])
    data = cursor.execute('SELECT city FROM city WHERE country_id=:country_id',{'country_id': id_miasta}).fetchall()
    cursor.close()
    return jsonify(data)

#kluczowy endpoint
@app.route('/miasto/<city_id>')
def single_city(city_id):
    db = get_db()
    data = db.execute(
        'SELECT country_id, city, city_id FROM city WHERE city_id = :city_id',
        {'city_id': city_id}).fetchone()
    return jsonify(data)

@app.route('/cities',methods=['POST'])
def dodajmiasto():
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
    return redirect("/miasto/"+str(city_id))

@app.route('/cities<per_page>&<page>', methods=['GET'])
def miasta_dziel(per_page,page):
    db = get_db()
    a = int(per_page)
    b = int(page)
    c = int((b*a)-a)
    cursor = db.cursor()
    data = cursor.execute('SELECT city FROM city LIMIT:a OFFSET:b',{'a': a, 'b' : c}).fetchall()
    cursor.close()
    return jsonify(data)


    

