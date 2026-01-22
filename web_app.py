from datetime import datetime, timezone
from pathlib import Path

import mysql.connector
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from Project.mongo import stats_top5_frequency, stats_last5_unique
from pymongo import MongoClient


from Project import queries
from Project.local_settings import dbconfig, MONGODB_URL_EDIT

PAGE_SIZE = 10

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
app = FastAPI()


def get_mysql_connection():
    return mysql.connector.connect(**dbconfig, autocommit=True)


def get_mongo_collection():
    client = MongoClient(MONGODB_URL_EDIT)
    db = client["ich_edit"]
    return db["final_project_010825-ptm_kateryna_dolinina"]


def log_query(search_type: str, params: dict, results_count: int) -> None:
    col = get_mongo_collection()
    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "search_type": search_type,
        "params": params,
        "results_count": results_count,
        }
    res = col.insert_one(doc)
    print("Mongo inserted:", res.inserted_id, doc)


def fetch_all(cursor):
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_genres():
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.SHOW_GENRES)
            return [r[0] for r in cursor.fetchall()]


def get_min_max_year():
    with get_mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(queries.MIN_MAX_YEAR)
            row = cursor.fetchone()
            return int(row[0]), int(row[1])


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    genres = ["All"] + get_genres()
    min_y, max_y = get_min_max_year()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "genres": genres, "min_y": min_y, "max_y": max_y},
    )


@app.get("/search/keyword", response_class=HTMLResponse)
def search_keyword(request: Request, keyword: str = "", page: int = 1):
    keyword = keyword.strip()
    offset = (page - 1) * PAGE_SIZE

    rows = []
    if keyword:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    queries.SEARCH_BY_KEYWORD,
            (f"%{keyword.lower()}%", PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

        log_query("keyword", {"keyword": keyword}, len(rows))

    has_more = len(rows) == PAGE_SIZE
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "title": "Search by keyword",
            "rows": rows,
            "page": page,
            "has_more": has_more,
            "next_url": f"/search/keyword?keyword={keyword}&page={page+1}",
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
    genre = genre.strip()
    offset = (page - 1) * PAGE_SIZE

    rows = []
    if genre and year_from and year_to:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                if genre == "All":
                    cursor.execute(
                        queries.SEARCH_BY_YEARS_ALL_GENRES,
                        (year_from, year_to, PAGE_SIZE, offset),
                    )
                else:
                    cursor.execute(
                        queries.SEARCH_BY_GENRE_YEARS,
                (genre, year_from, year_to, PAGE_SIZE, offset),
                    )
                rows = fetch_all(cursor)

        log_query(
            "genre__years_range",
            {"genre": genre, "years_range": f"{year_from}-{year_to}"},
            len(rows),
        )

    has_more = len(rows) == PAGE_SIZE
    next_url = (
        f"/search/genre?genre={genre}&year_from={year_from}&year_to={year_to}&page={page+1}"
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
    top5 = stats_top5_frequency()
    last5 = stats_last5_unique()


    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "top5": top5, "last5": last5},
    )