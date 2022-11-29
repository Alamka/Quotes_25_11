from random import choice
from flask import Flask
from flask import request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


quotes = [
    {
        "id": 3,
        "rating": 1,
        "author": "Rick Cook",
        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
    },
    {
        "id": 5,
        "rating": 3,
        "author": "Waldi Ravens",
        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
    },
    {
        "id": 6,
        "rating": 5,
        "author": "Mosher’s Law of Software Engineering",
        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
    },
    {
        "id": 8,
        "rating": 4,
        "author": "Yoggi Berra",
        "text": "В теории, теория и практика неразделимы. На практике это не так."
    },

]



def find_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            return quote
    return None


@app.route("/quotes/")
def get_quotes():
    return quotes


# /quotes/filter?author=Ivan&rating=5
@app.route("/quotes/filter/")
def filter_quotes():
    args = request.args
    author = args.get('author')
    rating = args.get('rating')

    quote_filter = []
    if None not in (author, rating):
        for quote in quotes:
            if quote["author"] == author and quote["rating"] == int(rating):
                quote_filter.append(quote)

    elif author is not None:
        for quote in quotes:
            if quote["author"] == author:
                quote_filter.append(quote)

    elif rating is not None:
        for quote in quotes:
            if quote["rating"] == int(rating):
                quote_filter.append(quote)

    if quote_filter:
        return quote_filter
    return "Not found", 404


@app.route("/quotes/count/")
def get_count_quotes():
    return {"count": len(quotes)}


@app.route("/quotes/<int:quote_id>/")
def get_quote_by_id(quote_id):
    quote = find_quote(quote_id)
    if quote:
        return quote

    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/random/")
def get_quote_random():
    return choice(quotes)


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
    new_quote.update({"id": quotes[-1]["id"] + 1})
    quotes.append(new_quote)
    return new_quote, 201


@app.route("/quotes/<int:quote_id>/", methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    quote = find_quote(quote_id)
    if quote:
        if "author" in new_data:
            quote["author"] = new_data["author"]
        if "text" in new_data:
            quote["text"] = new_data["text"]
        if "rating" in new_data and new_data["rating"] >= 1 and new_data["rating"] <= 5:
            quote["rating"] = new_data["rating"]
        return quote, 200

    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/<int:quote_id>/", methods=['DELETE'])
def delete_quote(quote_id):
    quote = find_quote(quote_id)
    if quote:
        quotes.remove(quote)
        return f"Quote with id {quote_id} is deleted.", 200

    return f"Quote with id={quote_id} not found", 404




if __name__ == "__main__":
    app.run(debug=True)