from datetime import datetime, timezone

import mongomock
from Project import mongo


def test_stats_pipelines_work(monkeypatch):
    client = mongomock.MongoClient()
    col = client["ich_edit"]["final_project_010825-ptm_kateryna_dolinina"]

# Подложим тестовые документы
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

    # Замокаем функцию, чтобы mongo.py работал с нашей коллекцией
    monkeypatch.setattr(mongo, "get_mongo_collection", lambda: col)

    top5 = mongo.stats_top5_frequency()
    last5 = mongo.stats_last5_unique()

    assert len(top5) <= 5
    assert len(last5) <= 5

    # Проверим, что в top5 есть count и params
    assert "count" in top5[0]
    assert "params" in top5[0]