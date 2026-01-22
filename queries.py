# queries.py
"""
SQL-запросы для работы с базой данных Sakila.

В этом модуле:
- хранятся ТОЛЬКО SQL-запросы
- нет логики Python
- нет подключения к базе

Используется:
- mysql_repo.py (для выполнения запросов)
- web_app.py (через mysql_repo)
- CLI flows (через mysql_repo)

Такое разделение упрощает поддержку и тестирование.
"""

# --------------------------------------------------
# Справочные запросы
# --------------------------------------------------

# Список всех жанров (используется в CLI и Web UI)
SHOW_GENRES = """
SELECT name
FROM category
ORDER BY name;
"""

# Минимальный и максимальный год выпуска фильмов в базе
# Используется для валидации пользовательского ввода
MIN_MAX_YEAR = """
SELECT MIN(release_year) AS min_y, MAX(release_year) AS max_y
FROM film;
"""

# --------------------------------------------------
# Поисковые запросы (с пагинацией)
# --------------------------------------------------

# Поиск фильмов по ключевому слову в названии
# Используется для постраничного вывода (LIMIT / OFFSET)
SEARCH_BY_KEYWORD = """
SELECT film_id, title, release_year
FROM film
WHERE LOWER(title) LIKE %s
ORDER BY title
LIMIT %s OFFSET %s;
"""

# Поиск фильмов по конкретному жанру и диапазону лет
SEARCH_BY_GENRE_YEARS = """
SELECT
    f.film_id,
    f.title,
    f.release_year,
    c.name AS genre
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE c.name = %s
AND f.release_year BETWEEN %s AND %s
ORDER BY f.release_year, f.title
LIMIT %s OFFSET %s;
"""

# Поиск фильмов по диапазону лет без фильтрации по жанру
# Используется для варианта "All genres"
SEARCH_BY_YEARS_ALL_GENRES = """
SELECT
    f.film_id,
    f.title,
    f.release_year,
    c.name AS genre
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE f.release_year BETWEEN %s AND %s
ORDER BY f.release_year, f.title
LIMIT %s OFFSET %s;
"""

# --------------------------------------------------
# COUNT-запросы (для логирования статистики)
# --------------------------------------------------

# Общее количество фильмов по ключевому слову
# Используется для записи results_count в MongoDB
COUNT_BY_KEYWORD = """
SELECT COUNT(*) AS cnt
FROM film
WHERE LOWER(title) LIKE %s;
"""

# Общее количество фильмов по жанру и диапазону лет
# DISTINCT нужен, чтобы избежать дублей из-за JOIN
COUNT_BY_GENRE_YEARS = """
SELECT COUNT(DISTINCT f.film_id) AS cnt
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE c.name = %s
    AND f.release_year BETWEEN %s AND %s;
"""

# Общее количество фильмов по диапазону лет (все жанры)
COUNT_BY_YEARS_ALL_GENRES = """
SELECT COUNT(DISTINCT f.film_id) AS cnt
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE f.release_year BETWEEN %s AND %s;
"""