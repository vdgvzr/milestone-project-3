import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from decouple import config

app = Flask(__name__)

DB_PASSWORD = config('PASSWORD')

app.config["MONGO_DBNAME"] = 'pen_hub'
app.config["MONGO_URI"] = 'mongodb+srv://vdgvzr:' +\
                           DB_PASSWORD +\
                          '@myfirstcluster.iop5x.mongodb.net/'\
                          'pen_hub?retryWrites=true&w=majority'

mongo = PyMongo(app)


def generateTitleCase(input_string):
    articles = ['a', 'an', 'the']
    conjunctions = ['and', 'but', 'for', 'nor', 'or', 'so', 'yet']
    prepositions = [
        'in', 'to', 'for', 'with', 'on', 'at',
        'from', 'by', 'about', 'as', 'into',
        'like', 'through', 'after', 'over',
        'between', 'out', 'against', 'during',
        'without', 'before', 'under', 'around',
        'among', 'of'
    ]
    lower_case = articles + conjunctions + prepositions
    output_string = ""
    input_list = input_string.split(" ")

    for word in input_list:
        if word in lower_case:
            output_string += word + " "
        else:
            temp = word.title()
            output_string += temp + " "
    return output_string


@app.route('/')
def home():
    return render_template(
        "index.html",
        books=mongo.db.books.find(),
        recents=mongo.db.books.find(),
        quotes=mongo.db.books.find(),
        genre=mongo.db.genre.find()
    )


@app.route('/add_book')
def add_book():
    return render_template("add-book.html", genre=mongo.db.genre.find())


@app.route('/add_genre')
def add_genre():
    return render_template("add-genre.html")


@app.route('/all_books')
def all_books():
    return render_template("all-books.html", books=mongo.db.books.find())


@app.route('/genre_list')
def genre_list():
    return render_template("genres.html", genre=mongo.db.genre.find())


@app.route('/book_review/<book_id>', methods=['GET'])
def book_review(book_id):
    rating_list = []

    get_review = mongo.db.review.find({"book_id": book_id})
    for i in get_review:
        rating_list.append(int(i['rating']))

    try:
        avg_rating = format(sum(rating_list)/len(rating_list), '.1f')
    except ZeroDivisionError:
        avg_rating = 0

    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    reviews = mongo.db.review.find({"book_id": book_id})
    no_of_docs = mongo.db.review.count_documents({"book_id": book_id})
    mongo.db.books.update(
        {"_id": ObjectId(book_id)},
        {"$set": {"rating": avg_rating}}
    )
    return render_template(
        'book-review.html',
        book=the_book,
        recent=the_book,
        genre=all_genre,
        review=reviews,
        average=avg_rating,
        review_amount=no_of_docs
    )


@app.route('/insert_book', methods=['POST'])
def insert_book():
    book = mongo.db.books
    book.insert_one(request.form.to_dict())
    return redirect(url_for('home'))


@app.route('/insert_genre', methods=['POST'])
def insert_genre():
    genre = mongo.db.genre
    genre.insert_one(request.form.to_dict())
    return redirect(url_for('home'))


@app.route('/edit_book/<book_id>')
def edit_book(book_id):
    the_book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    all_genre = mongo.db.genre.find()
    return render_template('edit-book.html', book=the_book, genre=all_genre)


@app.route('/add_review/<book_id>', methods=['POST'])
def add_review(book_id):
    review_object = request.form.to_dict()
    review_object['book_id'] = book_id
    mongo.db.review.insert_one(review_object)
    return redirect(url_for('book_review', book_id=book_id))


@app.route('/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    books = mongo.db.books
    books.update({"_id": ObjectId(book_id)},
                 {
                    'genre_name': request.form.get('genre_name'),
                    'image_url': request.form.get('image_url'),
                    'book_title': request.form.get('book_title'),
                    'book_author': request.form.get('book_author'),
                    'book_isbn': request.form.get('book_isbn'),
                    'book_blurb': request.form.get('book_blurb'),
                    'book_quote': request.form.get('book_quote'),
                    'rating': request.form.get('rating')
                 })
    return redirect(url_for('home'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    mongo.db.books.remove({'_id': ObjectId(book_id)})
    return redirect(url_for('home'))


@app.route('/genre/<genre_id>')
def genre(genre_id):
    the_genre = mongo.db.genre.find_one({"_id": ObjectId(genre_id)})
    all_books = mongo.db.books.find()
    return render_template(
        'genre.html',
        genre=the_genre,
        books=all_books,
    )


@app.route("/search_books")
def search_books():
    query = request.args.get("search")
    query = query.title()
    search_value = mongo.db.books.find({
        "$or": [
            {'book_title': {"$regex": query}},
            {'book_author': {"$regex": query}},
            {'book_isbn': {"$regex": query}}
        ]
    })
    no_of_docs = mongo.db.books.count_documents({
        "$or": [
            {'book_title': {"$regex": query}},
            {'book_author': {"$regex": query}},
            {'book_isbn': {"$regex": query}}
        ]
    })
    return render_template(
        "search-results.html",
        search=search_value,
        query=query,
        no_of_docs=no_of_docs,
    )


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
