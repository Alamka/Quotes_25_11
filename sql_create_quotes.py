import sqlite3



create_quotes = """
INSERT INTO
quotes (author, text, rating)
VALUES
('Rick Cook', 'Программирование сегодня — это гонка разработчиков программ...', 4),
('Waldi Ravens', 'Программирование на С похоже на быстрые танцы на только...', 3),
("Mosher’s Law of Software Engineering", "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.", 5),
("Yoggi Berra", "В теории, теория и практика неразделимы. На практике это не так.", 5);
"""

# Подключение в БД
connection = sqlite3.connect("test.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.execute(create_quotes)
# Фиксируем выполнение(транзакцию)
connection.commit()
# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()
