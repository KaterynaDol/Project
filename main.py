

# import mysql.connector
# from mongo import *
#
# import queries
# from local_settings import dbconfig, MONGODB_URL_EDIT

# main.py

"""
Main module.
Содержит:
- главное меню
- выбор действия
- запуск сценариев
"""

from flows import keyword_flow, genre_years_flow, stats_flow

# PAGE_SIZE = 10

text_main_menu = """
=== Movies Search ===
Please input 1, 2, 3 or 0:
1: Search by keyword (title)
2: Search by genre and years range
3: View statistics
0: Exit
"""

# text_stats_menu = """
# === Statistics ===
# 1: Top 5 by frequency
# 2: Last 5 unique searches
# 0: Back
# """


# def get_mysql_connection():
#     return mysql.connector.connect(**dbconfig)




def read_choice(prompt: str, allowed: set[str]) -> str:
    while True:
        value = input(prompt).strip()
        if value in allowed:
            return value
        print(f"Wrong input. Allowed: {', '.join(sorted(allowed))}")


# def print_movies(rows: list[dict]) -> None:
#     if not rows:
#         print("No results.")
#         return
#     for r in rows:
#         title = r.get("title")
#     year = r.get("release_year")
#     genre = r.get("genre")
#     if genre:
#         print(f"{title} ({year}) | {genre}")
#     else:
#         print(f"{title} ({year})")


# def ask_show_more() -> bool:
#     ans = input("Show next 10? (y/n): ").strip().lower()
#     return ans in {"y", "yes", "да", "д"}


# def fetch_all(cursor) -> list[dict]:
#     cols = [d[0] for d in cursor.description]
#     return [dict(zip(cols, row)) for row in cursor.fetchall()]


# def get_genres() -> list[str]:
#     with get_mysql_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(queries.SHOW_GENRES)
#             return [row[0] for row in cursor.fetchall()]


# def get_min_max_year() -> tuple[int, int]:
#     with get_mysql_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(queries.MIN_MAX_YEAR)
#             row = cursor.fetchone()
#             return int(row[0]), int(row[1])


# def search_by_keyword_flow() -> None:
#     keyword = input("Enter keyword: ").strip()
#     if not keyword:
#         print("Empty keyword. Back to menu.")
#         return

    # offset = 0
    # total = 0
    #
    # while True:
    #     with get_mysql_connection() as conn:
    #         with conn.cursor() as cursor:
    #             cursor.execute(
    #                 queries.SEARCH_BY_KEYWORD,
    #                 (f"%{keyword.lower()}%", PAGE_SIZE, offset),
    #             )
    #             rows = fetch_all(cursor)
    #
    #     print_movies(rows)
    #     total += len(rows)
    #
    #     if len(rows) < PAGE_SIZE:
    #         break
    #     if not ask_show_more():
    #         break
    #     offset += PAGE_SIZE
    #
    # log_query("keyword", {"keyword": keyword}, total)


# def parse_years_input(min_y: int, max_y: int) -> tuple[int, int]:
#     raw = input("Enter year or range (e.g. 2005-2012): ").strip()
#     if "-" in raw:
#         left, right = [x.strip() for x in raw.split("-", 1)]
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
#     if y1 < min_y or y2 > max_y:
#         raise ValueError(f"Years must be within {min_y}-{max_y}")
#     return y1, y2


# def search_by_genre_years_flow() -> None:
#     genres = get_genres()
#     min_y, max_y = get_min_max_year()
#
#     print("Genres:")
#     print(", ".join(genres))
#     print(f"Years in DB: {min_y}-{max_y}")
#
#     genre = input("Enter genre exactly: ").strip()
#     if genre not in genres:
#         print("Genre not found. Back to menu.")
#         return
#
#
#     while True:
#         try:
#             year_from, year_to = parse_years_input(min_y, max_y)
#             break
#         except ValueError as exc:
#             print(f"Error: {exc}")
#
#     offset = 0
#     total = 0
#
#     while True:
#         with get_mysql_connection() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute(
#                     queries.SEARCH_BY_GENRE_YEARS,
#                     (genre, year_from, year_to, PAGE_SIZE, offset),
#                 )
#                 rows = fetch_all(cursor)
#
#         print_movies(rows)
#         total += len(rows)
#
#         if len(rows) < PAGE_SIZE:
#             break
#         if not ask_show_more():
#             break
#         offset += PAGE_SIZE
#
#     log_query(
#         "genre__years_range",
#         {"genre": genre, "years_range": f"{year_from}-{year_to}"},
#         total,
#     )




# def stats_flow() -> None:
#     while True:
#         print(text_stats_menu)
#         choice = read_choice("Your choice: ", {"1", "2", "0"})
#         if choice == "1":
#             stats_top5_frequency()
#         elif choice == "2":
#             stats_last5_unique()
#         elif choice == "0":
#             return


# def main() -> None:
#     while True:
#         print(text_main_menu)
#         choice = read_choice("Your choice: ", {"1", "2", "3", "0"})
#
#         if choice == "1":
#             search_by_keyword_flow()
#         elif choice == "2":
#             search_by_genre_years_flow()
#         elif choice == "3":
#             stats_flow()
#         elif choice == "0":
#             print("Bye!")
#             return


def main() -> None:
    while True:
        print(text_main_menu)
        choice = read_choice("Your choice: ", {"1", "2", "3", "0"})

        if choice == "1":
            keyword_flow()
        elif choice == "2":
            genre_years_flow()
        elif choice == "3":
            stats_flow()
        elif choice == "0":
            print("Bye!")
            return


if __name__ == "__main__":
    main()
