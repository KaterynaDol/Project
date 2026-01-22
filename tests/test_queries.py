from Project import queries


def test_queries_are_strings():
    assert isinstance(queries.SHOW_GENRES, str)
    assert isinstance(queries.MIN_MAX_YEAR, str)
    assert isinstance(queries.SEARCH_BY_KEYWORD, str)
    assert isinstance(queries.SEARCH_BY_GENRE_YEARS, str)
    assert isinstance(queries.SEARCH_BY_YEARS_ALL_GENRES, str)


def test_queries_not_empty():
    assert "SELECT" in queries.SEARCH_BY_KEYWORD.upper()
    assert "LIMIT" in queries.SEARCH_BY_KEYWORD.upper()
    assert "OFFSET" in queries.SEARCH_BY_KEYWORD.upper()