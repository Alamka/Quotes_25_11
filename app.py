from pathlib import Path
from random import choice
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

    def __init__(self, author, text):
        self.author = author
        self.text = text

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
        setattr(quote, key, value)

    #if new_data.get("author"):
    #    quote.author = new_data["author"]
    #if new_data.get("text"):
    #    quote.text = new_data["text"]
    #if new_data.get("rate") and new_data["rate"] >= 1 and new_data["rate"] <= 5:
    #    quote.rate = new_data["rate"]

    db.session.commit()
    return quote.to_dict(), 201



@app.route("/quotes/<int:quote_id>/", methods=['DELETE'])
def delete_quote(quote_id):
    sql_quote = "DELETE FROM quotes WHERE id=?;"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql_quote, (quote_id, ))
    conn.commit()
    if cur.rowcount > 0:
        return f"Quote with id={quote_id} is deleted.", 200

    return f"Quote with id={quote_id} not found", 404









@app.route("/quotes/filter/")
def filter_quotes():
    args = request.args
    # /quotes/filter?author=Tom&rating=5
    author = args.get('author')
    rating = args.get('rating')

    cur = get_db().cursor()
    sql_dict = None
    if None not in (author, rating):
        sql_quote = "SELECT * from quotes WHERE author=? AND rating=?"
        sql_dict = (author, rating,)

    elif author is not None:
        sql_quote = "SELECT * from quotes WHERE author=?"
        sql_dict = (author, )

    elif rating is not None:
        sql_quote = "SELECT * from quotes WHERE rating=?"
        sql_dict = (rating, )

    quote_filter = []
    if sql_dict:
        cur.execute(sql_quote, sql_dict)
        values = cur.fetchall()
        if values:
            for value in values:
                quote_filter.append(to_dict(value))
            return quote_filter

    return "Not found", 404


@app.route("/quotes/count/")
def get_count_quotes():
    cur = get_db().cursor()
    sql_quote = "SELECT count(*) from quotes"
    cur.execute(sql_quote)
    row = cur.fetchone()

    return {"count": row[0]}


@app.route("/quotes/random/v1/")
def get_quote_random_v1():
    cur = get_db().cursor()
    sql_quote = "SELECT id from quotes"
    cur.execute(sql_quote)
    values = cur.fetchall()
    if values:
        quote_id = choice(values)[0]
        value = find_quote(quote_id)
        return to_dict(value)

    return f"Quotes not found", 404

@app.route("/quotes/random/v2/")
def get_quote_random_v2():
    cur = get_db().cursor()
    sql_quote = "SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1;"
    cur.execute(sql_quote)
    value = cur.fetchone()
    if value:
        return to_dict(value)

    return f"Quotes not found", 404



if __name__ == "__main__":
    app.run(debug=True)