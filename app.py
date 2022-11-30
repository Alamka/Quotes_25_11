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


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False)
    text = db.Column(db.String(255), unique=False)
    rate = db.Column(db.Integer)

    def __init__(self, author, text, rate=1):
        self.author = author
        self.text = text
        self.rate = rate

    def __repr__(self):
        return f"Quote a:{self.author} t:{self.text}"

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rate": self.rate
        }


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
    value = QuoteModel.query.get(quote_id)
    if value:
        return value.to_dict()

    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/", methods=['POST'])
def create_quote():
    data = request.json

    #quote = QuoteModel(author=data["author"], text=data["text"])
    quote = QuoteModel(**data)

    db.session.add(quote)
    db.session.commit()

    return quote.to_dict(), 201


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









@app.route("/quotes/filter/")
def filter_quotes():
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
    count_quotes = db.session.query(QuoteModel).count()
    return {"count": count_quotes}


@app.route("/quotes/random/")
def get_quote_random_v2():
    quote = db.session.query(QuoteModel).order_by(func.random()).first()
    if quote:
        return quote.to_dict()
    return f"Quotes not found", 404



if __name__ == "__main__":
    app.run(debug=True)