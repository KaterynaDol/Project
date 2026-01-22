#mongo.py
"""
Модуль работы с MongoDB.
Отвечает за:
- подключение к MongoDB
- агрегационные запросы для статистики поисков
"""

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


def stats_top5_frequency():
    """
    Top 5 запросов по частоте
    """
    col = get_mongo_collection()

    pipeline = [
        {"$sort": {"timestamp": 1}},
        {
            "$group": {
                "_id": {
                    "search_type": "$search_type",
                    "params": "$params"
                },
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
    Last 5 уникальных запросов,
    берём самые последние по времени.
    """
    col = get_mongo_collection()

    pipeline = [
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": {
                    "search_type": "$search_type",
                    "params": "$params"
                },

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


