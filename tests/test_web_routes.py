"""
Интеграционные тесты FastAPI-роутов.
Проверяют, что страницы приложения открываются и возвращают HTTP 200
без обращения к реальным базам данных.
"""


from fastapi.testclient import TestClient
from Project import web_app


def test_index_page(monkeypatch):
    # Подменяем функции, которые идут в MySQL
    monkeypatch.setattr(web_app, "get_genres", lambda: ["Action", "Comedy"])
    monkeypatch.setattr(web_app, "get_min_max_year", lambda: (1990, 2025))

    client = TestClient(web_app.app)
    resp = client.get("/")
    assert resp.status_code == 200


def test_stats_page(monkeypatch):
    # Подменяем статистику, чтобы не ходить в Mongo
    monkeypatch.setattr(web_app, "stats_top5_frequency", lambda: [])
    monkeypatch.setattr(web_app, "stats_last5_unique", lambda: [])

    client = TestClient(web_app.app)
    resp = client.get("/stats")
    assert resp.status_code == 200