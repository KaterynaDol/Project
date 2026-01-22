# flows.py
"""
Сценарии (flows) пользовательских действий для CLI (консольной версии).
Модуль содержит бизнес-логику приложения.

Здесь:
- поиск фильмов по ключевому слову (постранично)
- поиск по жанру и диапазону лет (постранично)
- просмотр статистики запросов
"""


from Project import queries
from Project.mysql_repo import (
    get_mysql_connection,
    fetch_all,
    get_genres,
    get_min_max_year
)
from Project.mongo import (
    stats_top5_frequency,
    stats_last5_unique,
    log_query
)

# Количество фильмов на страницу (pagination)
PAGE_SIZE = 10


# ====== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======

def print_movies(rows: list[dict]) -> None:
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
    """Спрашивает пользователя, показывать ли следующую страницу."""
    ans = input(f"Show next {PAGE_SIZE}? (y/n): ").strip().lower()
    return ans in {"y", "yes", "да", "д"}


def parse_years_range(raw: str, min_y: int, max_y: int) -> tuple[int, int]:
    """
    Парсит ввод года или диапазона лет.
    Проверяет границы (min_y..max_y)
    """
    raw = raw.strip()

    if "-" in raw:
        left, right = [x.strip() for x in raw.split("-", 1)]
        if not left.isdigit() or not right.isdigit():
            raise ValueError("Wrong format.")
        y1, y2 = int(left), int(right)
    else:
        if not raw.isdigit():
            raise ValueError("Wrong format.")
        y1 = y2 = int(raw)

    # Нормализуем порядок (если ввели наоборот)
    if y1 > y2:
        y1, y2 = y2, y1

    # Проверяем границы, чтобы пользователь не вводил год вне базы
    if y1 < min_y or y2 > max_y:
        raise ValueError(f"Years must be within {min_y}-{max_y}")

    return y1, y2


def parse_years_input(min_y: int, max_y: int) -> tuple[int, int]:
    raw = input("Enter year or range (e.g. 2005-2012): ").strip()
    return parse_years_range(raw, min_y, max_y)


# ====== FLOW: ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ ======

def keyword_flow() -> None:
    """Сценарий поиска фильмов по ключевому слову."""
    keyword = input("Enter keyword: ").strip()
    if not keyword:
        print("Empty keyword. Back to menu.")
        return

    offset = 0
    shown_count = 0  # сколько результатов реально показали пользователю за весь запрос

    while True:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    queries.SEARCH_BY_KEYWORD,
                    (f"%{keyword.lower()}%", PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

        print_movies(rows)
        shown_count += len(rows)

        # Если пришло меньше PAGE_SIZE - больше результатов нет
        if len(rows) < PAGE_SIZE:
            break

        # Если пользователь не хочет дальше - заканчиваем
        if not ask_show_more():
            break

        offset += PAGE_SIZE

    # Логирование запроса в MongoDB
    log_query("keyword", {"keyword": keyword}, shown_count)


# ====== FLOW: ПОИСК ПО ЖАНРУ И ГОДАМ ======

def genre_years_flow() -> None:
    """Сценарий поиска фильмов по жанру и диапазону лет."""
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
    shown_count = 0

    while True:
        with get_mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    queries.SEARCH_BY_GENRE_YEARS,
                    (genre, year_from, year_to, PAGE_SIZE, offset),
                )
                rows = fetch_all(cursor)

        print_movies(rows)
        shown_count += len(rows)

        if len(rows) < PAGE_SIZE:
            break
        if not ask_show_more():
            break

        offset += PAGE_SIZE

    # Логирование запроса в MongoDB
    log_query(
        "genre__years_range",
        {"genre": genre, "years_range": f"{year_from}-{year_to}"},
        shown_count,
    )


# ====== FLOW: СТАТИСТИКА ======

def stats_flow() -> None:
    """Сценарий просмотра статистики запросов."""
    while True:
        print(
            """
=== Statistics ===
1: Top 5 by frequency
2: Last 5 unique searches
0: Back
"""
        )
        choice = input("Your choice: ").strip()

        if choice == "1":
            rows = stats_top5_frequency()
            for r in rows:
                print(
                    f"{r.get('count')}x | {r.get('search_type')} | {r.get('params')} "
                    f"| rows={r.get('results_count')} | {r.get('timestamp')}"
                )

        elif choice == "2":
            rows = stats_last5_unique()
            for r in rows:
                print(
                    f"{r.get('search_type')} | {r.get('params')} "
                    f"| rows={r.get('results_count')} | {r.get('timestamp')}"
                )

        elif choice == "0":
            return
