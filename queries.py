SHOW_GENRES = """
SELECT name
FROM category
ORDER BY name;
"""

MIN_MAX_YEAR = """
SELECT MIN(release_year) AS min_y, MAX(release_year) AS max_y
FROM film;
"""

SEARCH_BY_KEYWORD = """
SELECT film_id, title, release_year
FROM film
WHERE LOWER(title) LIKE %s
ORDER BY title
LIMIT %s OFFSET %s;
"""

SEARCH_BY_GENRE_YEARS = """
SELECT f.film_id, f.title, f.release_year, c.name AS genre
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE c.name = %s
AND f.release_year BETWEEN %s AND %s
ORDER BY f.release_year, f.title
LIMIT %s OFFSET %s;
"""

SEARCH_BY_YEARS_ALL_GENRES = """
SELECT f.film_id, f.title, f.release_year, c.name AS genre
FROM film f
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE f.release_year BETWEEN %s AND %s
ORDER BY f.release_year, f.title
LIMIT %s OFFSET %s;
"""