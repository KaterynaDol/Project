
"""
#flows.py

Сценарии (flows) пользовательских действий.
Модуль содержит бизнес-логику приложения, но НЕ меню верхнего уровня.

Здесь:
- сценарии поиска фильмов
- сценарий просмотра статистики
- постраничный вывод
"""

from typing import List, Dict

from mysql_repo import (
    get_mysql_connection,
    fetch_all,
    get_genres,
    get_min_max_year
)
from mongo import (
    log_query,
    stats_top5_frequency,
    stats_last5_unique,
)
import queries


# Количество фильмов на страницу (pagination)
PAGE_SIZE = 10


# ====== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======

def print_movies(rows: List[Dict]) -> None:
    """
    Печатает список фильмов в читаемом виде.
    """
    if not rows:
        print("No results.")
        return

    for r in rows:
        title = r.get("title")
        year = r.get("release_year")
        genre = r.get("genre")

    if genre:
        print(f"{title} ({year}) | {genre}")
    else:
        print(f"{title} ({year})")


def ask_show_more() -> bool:
    """
    Спрашивает пользователя, показывать ли следующую страницу.
    """
    ans = input("Show next 10? (y/n): ").strip().lower()
    return ans in {"y", "yes", "да", "д"}


def parse_years_input(min_y: int, max_y: int) -> tuple[int, int]:
    """
    Парсит ввод года или диапазона лет.
    """
    raw = input("Enter year or range (e.g. 2005-2012): ").strip()

    if "-" in raw:
        left, right = [x.strip() for x in raw.split("-", 1)]
        if not left.isdigit() or not right.isdigit():
            raise ValueError("Wrong format.")
        y1, y2 = int(left), int(right)
    else:
        if not raw.isdigit():
            raise ValueError("Wrong format.")
        y1 = y2 = int(raw)

    if y1 > y2:
        y1, y2 = y2, y1

    if y1 < min_y or y2 > max_y:
        raise ValueError(f"Years must be within {min_y}-{max_y}")

    return y1, y2


# ====== FLOW: ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ ======

def keyword_flow() -> None:
    """
    Сценарий поиска фильмов по ключевому слову.
    """
    keyword = input("Enter keyword: ").strip()
    if not keyword:
        print("Empty keyword. Back to menu.")
        return

    offset = 0
    total = 0

    while True:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    queries.SEARCH_BY_KEYWORD,
                    (f"%{keyword.lower()}%", PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

        print_movies(rows)
        total += len(rows)

        if len(rows) < PAGE_SIZE:
            break
        if not ask_show_more():
            break

        offset += PAGE_SIZE

    # логирование запроса в MongoDB
    log_query("keyword", {"keyword": keyword}, total)


# ====== FLOW: ПОИСК ПО ЖАНРУ И ГОДАМ ======

def genre_years_flow() -> None:
    """
    Сценарий поиска фильмов по жанру и диапазону лет.
    """
    genres = get_genres()
    min_y, max_y = get_min_max_year()

    print("Genres:")
    print(", ".join(genres))
    print(f"Years in DB: {min_y}-{max_y}")

    genre = input("Enter genre exactly: ").strip()
    if genre not in genres:
        print("Genre not found. Back to menu.")
        return

    while True:
        try:
            year_from, year_to = parse_years_input(min_y, max_y)
            break
        except ValueError as exc:
            print(f"Error: {exc}")

    offset = 0
    total = 0

    while True:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    queries.SEARCH_BY_GENRE_YEARS,
                    (genre, year_from, year_to, PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

        print_movies(rows)
        total += len(rows)

        if len(rows) < PAGE_SIZE:
            break
        if not ask_show_more():
            break

        offset += PAGE_SIZE

    # логирование запроса в MongoDB
    log_query(
        "genre_years",
        {"genre": genre, "years_range": f"{year_from}-{year_to}"},
        total,
    )


# ====== FLOW: СТАТИСТИКА ======

def stats_flow() -> None:
    """
    Сценарий просмотра статистики запросов.
    """
    while True:
        print("""
=== Statistics ===
1: Top 5 by frequency
2: Last 5 unique searches
0: Back
""")
        choice = input("Your choice: ").strip()

        if choice == "1":
            rows = stats_top5_frequency()
            for r in rows:
                print(
                    f"{r['count']}x | {r['search_type']} | {r['params']} "
                    f"| rows={r['results_count']} | {r['timestamp']}"
                )

        elif choice == "2":
            rows = stats_last5_unique()
            for r in rows:
                print(
                    f"{r['search_type']} | {r['params']} "
                    f"| rows={r['results_count']} | {r['timestamp']}"
                )

        elif choice == "0":
            return


# """
# Flows (сценарии).
# Здесь логика программы, но БЕЗ главного меню.
# """
#
# from mysql_repo import (
#     get_genres,
#     get_min_max_year,
#     search_by_keyword,
#     search_by_genre_years,
# )
# from mongo import (
#     log_query, stats_top5_frequency, stats_last5_unique
# )
# import queries
#
# PAGE_SIZE = 10
#
#
# def print_movies(rows: list[dict]) -> None:
#     """Печать фильмов в консоль."""
#     if not rows:
#         print("No results.")
#         return
#
#     for r in rows:
#         title = r.get("title")
#         year = r.get("release_year")
#         genre = r.get("genre")
#         if genre:
#             print(f"{title} ({year}) | {genre}")
#         else:
#             print(f"{title} ({year})")
#
#
# def ask_show_more() -> bool:
#     """Спросить, показывать ли следующую страницу."""
#         ans = input("Show next 10? (y/n): ").strip().lower()
#         return ans in {"y", "yes", "да", "д"}
#
#
# def parse_years_input(min_y: int, max_y: int) -> tuple[int, int]:
#     """Парсинг и валидация диапазона лет."""
#     raw = input("Enter year or range (e.g. 2005-2012): ").strip()
#
#     if "-" in raw:
#         left, right = raw.split("-", 1)
#         if not left.isdigit() or not right.isdigit():
#             raise ValueError("Wrong format.")
#         y1, y2 = int(left), int(right)
#     else:
#         if not raw.isdigit():
#             raise ValueError("Wrong format.")
#         y1 = y2 = int(raw)
#
#     if y1 > y2:
#         y1, y2 = y2, y1
#
#     if y1 < min_y or y2 > max_y:
#         raise ValueError(f"Years must be within {min_y}-{max_y}")
#
#     return y1, y2
#
#
# def keyword_flow() -> None:
#     """Поиск по ключевому слову + логирование."""
#     keyword = input("Enter keyword: ").strip()
#     if not keyword:
#         print("Empty keyword.")
#         return
#
#     offset = 0
#     total = 0
#
#     while True:
#         rows = search_by_keyword(keyword, PAGE_SIZE, offset)
#         print_movies(rows)
#         total += len(rows)
#
#         if len(rows) < PAGE_SIZE:
#             break
#         if not ask_show_more():
#             break
#
#         offset += PAGE_SIZE
#
#     log_query("keyword", {"keyword": keyword}, total)
#
#
# def genre_years_flow() -> None:
#     """Поиск по жанру и годам + логирование."""
#     genres = get_genres()
#     min_y, max_y = get_min_max_year()
#
#     print("Genres:")
#     print(", ".join(genres))
#     print(f"Years in DB: {min_y}-{max_y}")
#
#     genre = input("Enter genre exactly: ").strip()
#     if genre not in genres:
#         print("Genre not found.")
#         return
#
#     while True:
#         try:
#             year_from, year_to = parse_years_input(min_y, max_y)
#             break
#         except ValueError as e:
#             print(f"Error: {e}")
#
#     offset = 0
#     total = 0
#
#     while True:
#         rows = search_by_genre_years(
#         genre, year_from, year_to, PAGE_SIZE, offset
#         )
#         print_movies(rows)
#         total += len(rows)
#
#         if len(rows) < PAGE_SIZE:
#             break
#         if not ask_show_more():
#             break
#
#         offset += PAGE_SIZE
#
#     log_query(
#     "genre__years_range",
#     {"genre": genre, "years_range": f"{year_from}-{year_to}"},
#     total,
#     )
#
#
# def stats_flow() -> None:
#     """Работа со статистикой MongoDB."""
#     print("\n=== Statistics ===")
#     print("1: Top 5 by frequency")
#     print("2: Last 5 unique searches")
#     print("0: Back")
#
#     choice = input("Your choice: ").strip()
#
#     if choice == "1":
#         for r in stats_top5_frequency():
#             print(
#                 f"{r['count']}x | {r['search_type']} | {r['params']} "
#                 f"| rows={r['results_count']} | {r['timestamp']}"
#             )
#     elif choice == "2":
#         for r in stats_last5_unique():
#             print(
#                 f"{r['search_type']} | {r['params']} "
#                 f"| rows={r['results_count']} | {r['timestamp']}"
#             )