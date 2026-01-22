"""
Unit-тесты для модуля mongo.py (статистика запросов).

Цель теста:
- проверить, что агрегационные пайплайны MongoDB работают корректно
- не использовать реальную MongoDB (используется mongomock)
- убедиться, что функции stats_top5_frequency и stats_last5_unique
возвращают ожидаемую структуру данных
"""

from datetime import datetime, timezone

import mongomock
from Project import mongo


def test_stats_pipelines_work(monkeypatch):
    """
    Проверяем работу агрегатных запросов MongoDB.

    Используем mongomock, чтобы:
    - не подключаться к реальной базе
    - полностью изолировать тест
    """

    # Создаём mock-клиент MongoDB в памяти
    client = mongomock.MongoClient()
    col = client["ich_edit"]["final_project_010825-ptm_kateryna_dolinina"]

    # Подкладываем тестовые документы,
    # имитирующие реальные логи пользовательских запросов
    col.insert_many([
        {
            "timestamp": datetime(2026, 1, 21, tzinfo=timezone.utc).isoformat(),
            "search_type": "keyword",
            "params": {"keyword": "academy"},
            "results_count": 2,
        },
        {
            "timestamp": datetime(2026, 1, 21, 12, tzinfo=timezone.utc).isoformat(),
            "search_type": "keyword",
            "params": {"keyword": "academy"},
            "results_count": 2,
        },
        {
            "timestamp": datetime(2026, 1, 20, tzinfo=timezone.utc).isoformat(),
            "search_type": "genre__years_range",
            "params": {"genre": "All", "years_range": "1990-2025"},
            "results_count": 10,
        },
    ])

    # Подменяем функцию get_mongo_collection,
    # чтобы mongo.py работал с mock-коллекцией, а не с реальной БД
    monkeypatch.setattr(mongo, "get_mongo_collection", lambda: col)

    # Вызываем функции статистики
    top5 = mongo.stats_top5_frequency()
    last5 = mongo.stats_last5_unique()

    # Проверяем, что количество результатов не превышает лимиты
    assert len(top5) <= 5
    assert len(last5) <= 5

    # Проверяем структуру результата top5
    # (наличие count и params после агрегации)
    assert "count" in top5[0]
    assert "params" in top5[0]
