import pytest
from Project.flows import parse_years_range


def test_parse_single_year():
    assert parse_years_range("2010", 1990, 2025) == (2010, 2010)


def test_parse_range():
    assert parse_years_range("2005-2012", 1990, 2025) == (2005, 2012)


def test_parse_swapped_range():
    assert parse_years_range("2012-2005", 1990, 2025) == (2005, 2012)


def test_parse_out_of_bounds():
    with pytest.raises(ValueError):
        parse_years_range("1800-1900", 1990, 2025)


def test_parse_wrong_format():
    with pytest.raises(ValueError):
        parse_years_range("20aa-2012", 1990, 2025)