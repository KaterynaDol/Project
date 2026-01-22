# mysql_repo.py
"""
MySQL repository.
Модуль отвечает ТОЛЬКО за работу с MySQL:
- подключение к базе
- выполнение SQL-запросов
- преобразование результатов в удобный формат
"""

import mysql.connector

from Project import queries
from Project.local_settings import dbconfig


def get_mysql_connection():
    """Создаёт соединение с MySQL."""
    return mysql.connector.connect(**dbconfig)


def fetch_all(cursor) -> list[dict]:
    """
    Преобразует результат cursor.fetchall() в список словарей.
    Ключи словаря - названия колонок.
    """
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_genres() -> list[str]:
    """Возвращает список жанров."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.SHOW_GENRES)
            return [row[0] for row in cursor.fetchall()]


def get_min_max_year() -> tuple[int, int]:
    """Минимальный и максимальный год в базе."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.MIN_MAX_YEAR)
            row = cursor.fetchone()
            return int(row[0]), int(row[1])


def search_by_keyword(keyword: str, limit: int, offset: int) -> list[dict]:
    """Поиск фильмов по ключевому слову."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                queries.SEARCH_BY_KEYWORD,
        (f"%{keyword.lower()}%", limit, offset),
            )
            return fetch_all(cursor)


def search_by_genre_years(
        genre: str, year_from: int, year_to: int, limit: int, offset: int
) -> list[dict]:
    """Поиск фильмов по жанру и диапазону лет."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                queries.SEARCH_BY_GENRE_YEARS,
        (genre, year_from, year_to, limit, offset),
            )
            return fetch_all(cursor)
