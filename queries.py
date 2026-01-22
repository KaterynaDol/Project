#queries.py
"""
SQL - запросы для работы с базой данных Sakila.
Все запросы вынесены в отдельный модуль для удобства
поддержки и повторного использования.
"""

#Список всех жанров
SHOW_GENRES = """
SELECT name
FROM category
ORDER BY name;
"""

#Минимальный и максимальный год выпуска фильмов
MIN_MAX_YEAR = """
SELECT MIN(release_year) AS min_y, MAX(release_year) AS max_y
FROM film;
"""

#Поиск фильмов по ключевому слову в названии
#Используется для постраничного вывода (LIMIT / OFFSET)
SEARCH_BY_KEYWORD = """
SELECT film_id, title, release_year
FROM film
WHERE LOWER(title) LIKE %s
ORDER BY title
LIMIT %s OFFSET %s;
"""

#Поиск фильмов по конкретному жанру и диапазону лет
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

#Поиск фильмов по диапазону лет без фильтрации
#Используется для варианта "All genres"
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