"""
Unit-тесты для функции parse_years_range из модуля flows.py.

Цель тестов:
- проверить корректный разбор пользовательского ввода года
- проверить работу с диапазонами лет
- убедиться, что функция корректно обрабатывает ошибки ввода

Тестируется ТОЛЬКО чистая функция без ввода/вывода и без работы с БД.
"""

import pytest
from Project.flows import parse_years_range


def test_parse_single_year():
    """
    Пользователь вводит один год.
    Ожидаем, что функция вернёт кортеж (year, year).
    """
    assert parse_years_range("2010", 1990, 2025) == (2010, 2010)


def test_parse_range():
    """
    Пользователь вводит корректный диапазон лет.
    Ожидаем корректный кортеж (from, to).
    """
    assert parse_years_range("2005-2012", 1990, 2025) == (2005, 2012)


def test_parse_swapped_range():
    """
    Пользователь вводит диапазон в обратном порядке.
    Функция должна нормализовать порядок годов.
    """
    assert parse_years_range("2012-2005", 1990, 2025) == (2005, 2012)


def test_parse_out_of_bounds():
    """
    Пользователь вводит диапазон за пределами базы данных.
    Ожидаем выброс исключения ValueError.
    """
    with pytest.raises(ValueError):
        parse_years_range("1800-1900", 1990, 2025)


def test_parse_wrong_format():
    """
    Пользователь вводит строку с неверным форматом.
    Ожидаем выброс исключения ValueError.
    """
    with pytest.raises(ValueError):
        parse_years_range("20aa-2012", 1990, 2025)
