import sqlite3
from pathlib import Path
from random import choice
from flask import Flask, request, g

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"


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


def find_quote(quote_id):
    cur = get_db().cursor()
    select_quote = "SELECT * from quotes WHERE id=?"
    cur.execute(select_quote, (quote_id,))
    value = cur.fetchone()
    # закрывать курсор не надо, потому что у нас простое приложение
    # при закрытии подключения курсоры закрываются автоматически
    # cur.close()
    return value


def to_dict(value):
    keys = ["id", "author", "text", "rating"]
    return dict(zip(keys, value))


@app.route("/quotes/")
def get_quotes():
    cur = get_db().cursor()
    select_quotes = "SELECT * from quotes"
    cur.execute(select_quotes)
    values = cur.fetchall()
    quotes = []
    for value in values:
        quotes.append(to_dict(value))

    return quotes


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


@app.route("/quotes/<int:quote_id>/")
def get_quote_by_id(quote_id):
    value = find_quote(quote_id)

    # Если нужно проверить конкретно на None
    # if value is not None:

    if value:
        return to_dict(value)

    return f"Quote with id={quote_id} not found", 404


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



@app.route("/quotes/", methods=['POST'])
def create_quote():
    data = request.json

    new_quote = {}
    if "author" in data:
        new_quote.update({"author": data["author"]})
    else:
        return f"New quote must have 'author'", 404
    if "text" in data:
        new_quote.update({"text": data["text"]})
    else:
        return f"New quote must have 'text'", 404
    if "rating" in data and data["rating"] >=1 and data["rating"] <= 5:
        new_quote.update({"rating": data["rating"]})
    else:
        new_quote.update({"rating": 1})

    sql_quote = "INSERT INTO quotes (author,text,rating) VALUES (?, ?, ?)"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql_quote, (new_quote["author"], new_quote["text"], new_quote["rating"]))
    conn.commit()

    new_quote["id"] = cur.lastrowid
    return new_quote, 201


@app.route("/quotes/<int:quote_id>/", methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json

    update_quote = "UPDATE quotes SET {} WHERE id=?"
    quote = []
    msg = []
    if new_data.get("author"):
        quote.append(new_data["author"])
        msg.append("author = ?")
    if new_data.get("text"):
        quote.append(new_data["text"])
        msg.append("text = ?")
    if new_data.get("rating") and new_data["rating"] >= 1 and new_data["rating"] <= 5:
        quote.append(new_data["rating"])
        msg.append("rating = ?")

    if len(quote) == 0:
        return f"No data to change", 404

    quote.append(quote_id)

    conn = get_db()
    cur = conn.cursor()
    sql_quote = update_quote.format(", ".join(msg))
    cur.execute(sql_quote, (quote))
    conn.commit()
    if cur.rowcount > 0:
        value = find_quote(quote_id)
        if value:
            return to_dict(value), 200

    return f"Quote with id={quote_id} not found", 404


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




if __name__ == "__main__":
    app.run(debug=True)