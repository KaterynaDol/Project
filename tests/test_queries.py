"""
Unit-тесты для модуля queries.py.

Цель тестов:
- убедиться, что все SQL-запросы объявлены
- проверить, что запросы являются строками
- базово проверить корректность структуры SQL (без выполнения в БД)

Эти тесты НЕ подключаются к базе данных
и проверяют только содержимое Python-модуля.
"""

from Project import queries


def test_queries_are_strings():
    """
    Проверяем, что все SQL-запросы объявлены как строки.
    Это защищает от случайных изменений типа (None, list и т.п.).
    """
    assert isinstance(queries.SHOW_GENRES, str)
    assert isinstance(queries.MIN_MAX_YEAR, str)
    assert isinstance(queries.SEARCH_BY_KEYWORD, str)
    assert isinstance(queries.SEARCH_BY_GENRE_YEARS, str)
    assert isinstance(queries.SEARCH_BY_YEARS_ALL_GENRES, str)


def test_queries_not_empty():
    """
    Базовая проверка структуры SQL-запроса поиска по ключевому слову.

    Проверяем, что запрос:
    - содержит SELECT
    - использует LIMIT и OFFSET для пагинации

    Это не полноценная проверка SQL,
    но защита от случайного удаления важных частей запроса.
    """
    assert "SELECT" in queries.SEARCH_BY_KEYWORD.upper()
    assert "LIMIT" in queries.SEARCH_BY_KEYWORD.upper()
    assert "OFFSET" in queries.SEARCH_BY_KEYWORD.upper()
