import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from decouple import config

app = Flask(__name__)

DB_PASSWORD = config('PASSWORD')

app.config["MONGO_DBNAME"] = 'pen_hub'
app.config["MONGO_URI"] = 'mongodb+srv://vdgvzr:' + DB_PASSWORD + '@myfirstcluster.iop5x.mongodb.net/pen_hub?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_books')
def get_books():
    return render_template("books.html", books=mongo.db.books.find())


@app.route('/add_book')
def add_book():
    return render_template("add-book.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
