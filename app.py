from pathlib import Path
from random import choice
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.expression import func

BASE_DIR = Path(__file__).parent
#DATABASE = BASE_DIR / "test.db"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    surname = db.Column(db.String(64))
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    #def __init__(self, name):
    #    self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text
        }



# AUTHORS handlers

@app.route("/authors/")
def get_authors():
    authors = AuthorModel.query.all()
    author_dict = []
    for author in authors:
        author_dict.append(author.to_dict())
    return author_dict


@app.route("/authors/<int:author_id>/")
def get_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author:
        return author.to_dict()

    return f"Author with id={author_id} not found", 404


@app.route("/authors/", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(**author_data)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


@app.route("/authors/<int:author_id>/", methods=["PUT"])
def edit_author(author_id):
    new_data = request.json

    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404

    for key, value in new_data.items():
        setattr(author, key, value)

    db.session.commit()
    return author.to_dict(), 201


@app.route("/authors/<int:author_id>/", methods=['DELETE'])
def delete_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404
    db.session.delete(author)
    db.session.commit()

    return f"Author with id={author_id} is deleted.", 200




# QUOTES handlers

@app.route("/quotes/")
#       to_dict()      flask
# object --------> dict -----> json
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/<int:quote_id>/")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote:
        return quote.to_dict()
    return f"Quote with id={quote_id} not found", 404


@app.route("/authors/<int:author_id>/quotes/")
def get_quotes_by_author_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404
    quotes = author.quotes.all()
    if len(quotes) == 0:
        return f"Not found quotes by author with id={author_id}", 404
    quote_dict = []
    for quote in quotes:
        quote_dict.append(quote.to_dict())
    return quote_dict


@app.route("/authors/<int:author_id>/quotes/", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404
    new_quote = request.json
    q = QuoteModel(author, **new_quote)
    db.session.add(q)
    db.session.commit()
    return q.to_dict(), 201


@app.route("/quotes/<int:quote_id>/", methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json

    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id={quote_id} not found", 404

    for key, value in new_data.items():
        #if key == "rate" and not (value >= 1 and value <= 5):
        #    continue
        setattr(quote, key, value)

    db.session.commit()
    return quote.to_dict(), 201


@app.route("/quotes/<int:quote_id>/", methods=['DELETE'])
def delete_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    db.session.delete(quote)
    db.session.commit()

    return f"Quote with id={quote_id} is deleted.", 200






# OTHER


@app.route("/quotes/filter/")
def filter_quotes():
    # TODO: edit
    args = request.args
    # /quotes/filter?author=Tom&rating=5
    author = args.get('author')
    rate = args.get('rate')

    if None not in (author, rate):
        quotes = db.session.query(QuoteModel)\
            .filter(QuoteModel.author == author, QuoteModel.rate == rate)\
            .all()

    elif author is not None:
        quotes = db.session.query(QuoteModel) \
            .filter(QuoteModel.author == author) \
            .all()

    elif rate is not None:
        quotes = db.session.query(QuoteModel) \
            .filter(QuoteModel.rate == rate) \
            .all()

    if not quotes:
        return "Not found", 404

    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/count/")
def get_count_quotes():
    # TODO: edit
    count_quotes = db.session.query(QuoteModel).count()
    return {"count": count_quotes}


@app.route("/quotes/random/")
def get_quote_random_v2():
    # TODO: edit
    quote = db.session.query(QuoteModel).order_by(func.random()).first()
    if quote:
        return quote.to_dict()
    return f"Quotes not found", 404



if __name__ == "__main__":
    app.run(debug=True)