# web_app.py
"""
FastAPI web-приложение для поиска фильмов (MySQL) и статистики запросов (MongoDB).

Функциональность:
- Главная страница: выбор жанра + диапазон лет, поиск по ключевому слову
- Результаты: пагинация по 10 фильмов
- Статистика: Top 5 по частоте и Last 5 unique (берётся из MongoDB)

Логирование:
- В MongoDB пишется 1 запись на 1 поиск (только при page == 1)
- results_count = общее количество найденных фильмов по запросу (total_count)
"""

from pathlib import Path

import mysql.connector
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from Project import queries
from Project.local_settings import dbconfig
from Project.mongo import (
    stats_top5_frequency,
    stats_last5_unique,
    log_query
)

# Количество результатов на странице (пагинация)
PAGE_SIZE = 10

# Абсолютный путь до директории, где лежит web_app.py
BASE_DIR = Path(__file__).resolve().parent

# Шаблоны находятся в папке templates рядом с web_app.py
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

# Экземпляр FastAPI-приложения
app = FastAPI()


# -------------------------
# MySQL helpers
# -------------------------

def get_mysql_connection():
    """Создаёт подключение к MySQL."""
    return mysql.connector.connect(**dbconfig, autocommit=True)


def fetch_all(cursor) -> list[dict]:
    """
    Преобразует результат cursor.fetchall() в список словарей:
    [{col1: val1, col2: val2, ...}, ...]
    """
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_genres() -> list[str]:
    """Возвращает список жанров из MySQL."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.SHOW_GENRES)
            return [r[0] for r in cursor.fetchall()]


def get_min_max_year() -> tuple[int, int]:
    """Возвращает минимальный и максимальный год релиза в базе."""
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.MIN_MAX_YEAR)
            row = cursor.fetchone()
            return int(row[0]), int(row[1])


# -------------------------
# Routes (страницы)
# -------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Главная страница с формой поиска"""
    genres = ["All"] + get_genres()
    min_y, max_y = get_min_max_year()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "genres": genres, "min_y": min_y, "max_y": max_y},
    )


@app.get("/search/keyword", response_class=HTMLResponse)
def search_keyword(request: Request, keyword: str = "", page: int = 1):
    """Поиск по ключевому слову (title)."""
    keyword = keyword.strip()
    offset = (page - 1) * PAGE_SIZE

    rows: list[dict] = []
    has_more = False

    if keyword:
        like_value = f"%{keyword.lower()}%"

        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                # 1) Достаём текущую страницу результатов
                cursor.execute(
                    queries.SEARCH_BY_KEYWORD,
                    (like_value, PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

                # 2) Логируем только первый заход (page=1), пишем общее кол-во найденных фильмов
                if page == 1:
                    cursor.execute(queries.COUNT_BY_KEYWORD, (like_value,))
                    total_count = int(cursor.fetchone()[0])
                    log_query("keyword", {"keyword": keyword}, total_count)

        has_more = len(rows) == PAGE_SIZE

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "title": "Search by keyword",
            "rows": rows,
            "page": page,
            "has_more": has_more,
            "next_url": f"/search/keyword?keyword={keyword}&page={page + 1}",
            "back_url": "/",
        },
    )


@app.get("/search/genre", response_class=HTMLResponse)
def search_genre(
        request: Request,
        genre: str = "",
        year_from: int = 0,
        year_to: int = 0,
        page: int = 1,
):
    """
    Поиск по жанру и диапазону лет.
    Если genre == "All" — используем запрос по всем жанрам в диапазоне лет.
    """
    genre = genre.strip()
    offset = (page - 1) * PAGE_SIZE

    rows: list[dict] = []
    has_more = False

    if genre and year_from and year_to:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                if genre == "All":
                    # 1) Выборка текущей страницы (все жанры)
                    cursor.execute(
                        queries.SEARCH_BY_YEARS_ALL_GENRES,
                        (year_from, year_to, PAGE_SIZE, offset),
                    )
                    rows = fetch_all(cursor)

                    # 2) Логируем один раз (page == 1) + считаем total_count
                    if page == 1:
                        cursor.execute(
                            queries.COUNT_BY_YEARS_ALL_GENRES,
                            (year_from, year_to),
                        )
                        total_count = int(cursor.fetchone()[0])
                        log_query(
                            "genre__years_range",
                            {"genre": genre, "years_range": f"{year_from}-{year_to}"},
                            total_count,
                        )
                else:
                    # 1) Выборка текущей страницы (конкретный жанр)
                    cursor.execute(
                        queries.SEARCH_BY_GENRE_YEARS,
                        (genre, year_from, year_to, PAGE_SIZE, offset),
                    )
                    rows = fetch_all(cursor)

                    # 2) Логируем один раз (page == 1) + считаем total_count
                    if page == 1:
                        cursor.execute(
                            queries.COUNT_BY_GENRE_YEARS,
                            (genre, year_from, year_to),
                        )
                        total_count = int(cursor.fetchone()[0])
                        log_query(
                            "genre__years_range",
                            {"genre": genre, "years_range": f"{year_from}-{year_to}"},
                            total_count,
                        )

        has_more = len(rows) == PAGE_SIZE

    next_url = (
        f"/search/genre?genre={genre}&year_from={year_from}"
        f"&year_to={year_to}&page={page + 1}"
    )

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "title": "Search by genre & years",
            "rows": rows,
            "page": page,
            "has_more": has_more,
            "next_url": next_url,
            "back_url": "/",
        },
    )


@app.get("/stats", response_class=HTMLResponse)
def stats(request: Request):
    """
    Страница статистики:
    - Top 5 по частоте (часто повторяющиеся запросы)
    - Last 5 unique (последние уникальные запросы)
    """
    top5 = stats_top5_frequency()
    last5 = stats_last5_unique()

    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "top5": top5, "last5": last5},
    )
