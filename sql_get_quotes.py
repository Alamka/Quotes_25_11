import sqlite3

select_quotes = "SELECT * from quotes"
# Подключение в БД
connection = sqlite3.connect("test.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.execute(select_quotes)

# Извлекаем результаты запроса
values = cursor.fetchall()
keys = ["id", "author", "text"]
quotes = []
for value in values:
    quote = dict(zip(keys, value))
    quotes.append(quote)

#quotes = dict(zip(keys, values))
print(f"{quotes=}")

# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()
