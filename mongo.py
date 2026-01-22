# mongo.py
"""
Модуль работы с MongoDB.
Отвечает за:
- подключение к MongoDB
- запись логов поисковых запросов (log_query)
- агрегирование статистики (top5_frequency, last5_unique)
"""

from datetime import datetime, timezone
from pymongo import MongoClient
from Project.local_settings import MONGODB_URL_EDIT

DB_NAME = "ich_edit"
COLLECTION_NAME = "final_project_010825-ptm_kateryna_dolinina"


def get_mongo_collection():
    """
    Возвращает объект коллекции MongoDB,
    в которой хранятся логи поисковых запросов.
    """
    client = MongoClient(MONGODB_URL_EDIT)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


def log_query(search_type: str, params: dict, results_count: int) -> None:
    """
    Логирует один поисковый запрос пользователя в MongoDB.

    Поля документа:
    - timestamp: время запроса в UTC (ISO format)
    - search_type: тип поиска ("keyword" / "genre__years_range")
    - params: параметры поиска (keyword / genre / years_range)
    - results_count: количество найденных фильмов по запросу
    (в Web-версии это total_count, в CLI может быть количество показанных результатов)
    """
    col = get_mongo_collection()
    col.insert_one(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
        }
    )


def stats_top5_frequency():
    """
    Возвращает Top 5 запросов по частоте (самые популярные).

    Логика:
    - группируем по (search_type + params)
    - считаем количество повторов (count)
    - сортируем по убыванию count, затем по времени
    """
    col = get_mongo_collection()

    pipeline = [
        # Сортировка по времени нужна, чтобы $last брал "последнюю" запись корректно
        {"$sort": {"timestamp": 1}},
        {
            "$group": {
                "_id": {"search_type": "$search_type", "params": "$params"},
                "count": {"$sum": 1},
                "search_type": {"$last": "$search_type"},
                "params": {"$last": "$params"},
                "results_count": {"$last": "$results_count"},
                "timestamp": {"$max": "$timestamp"},
            }
        },
        {"$sort": {"count": -1, "timestamp": -1}},
        {"$limit": 5},
    ]

    return list(col.aggregate(pipeline))


def stats_last5_unique():
    """
    Возвращает 5 последних уникальных запросов (Last 5 unique).

    Логика:
    - сортируем по времени (новые сверху)
    - группируем по (search_type + params) и берём первый (самый новый)
    - снова сортируем по timestamp и ограничиваем 5
    """
    col = get_mongo_collection()

    pipeline = [
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": {"search_type": "$search_type", "params": "$params"},
                "search_type": {"$first": "$search_type"},
                "params": {"$first": "$params"},
                "results_count": {"$first": "$results_count"},
                "timestamp": {"$first": "$timestamp"},
            }
        },
        {"$sort": {"timestamp": -1}},
        {"$limit": 5},
    ]

    return list(col.aggregate(pipeline))
