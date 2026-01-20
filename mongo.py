import json
from local_settings import MONGODB_URL_EDIT
from pymongo import MongoClient
from datetime import datetime, timezone

def get_mongo_collection():
    client = MongoClient(MONGODB_URL_EDIT)
    db = client["ich_edit"]
    return db["final_project_010825-ptm_kateryna_dolinina"]


def log_query(search_type: str, params: dict, results_count: int) -> None:
    try:
        col = get_mongo_collection()

        params_text = json.dumps(params, ensure_ascii=False, sort_keys=True)
        key = f"{search_type} | {params_text}"

        col.insert_one(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "search_type": search_type,
                "params": params,
                "key": key,
                "results_count": results_count,
            }
        )
    except Exception as e:
        print(f"[WARN] MongoDB logging failed: {e}")


def stats_top5_frequency() -> None:
    try:
        col = get_mongo_collection()
        pipeline = [
            {"$match": {"key": {"$exists": True}}},
            {
                "$group": {
                    "_id": "$key",
                    "count": {"$sum": 1},
                    "search_type": {"$first": "$search_type"},
                    "params": {"$first": "$params"},
                    "results_count": {"$first": "$results_count"},
                    "timestamp": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"count": -1, "timestamp": -1}},
            {"$limit": 5},
        ]

        # for r in col.aggregate(pipeline):
        #     print(f"{r['count']}x | {r['search_type']} | {r['params']} | rows={r['results_count']} | {r['timestamp']}")

        return list(col.aggregate(pipeline))

    except Exception as e:
        print(f"[ERROR] MongoDB stats failed: {e}")
        print("Tip: check MongoDB is running and mongo_config is correct.")


def stats_last5_unique() -> None:
    try:
        col = get_mongo_collection()
        pipeline = [
            {"$match": {"key": {"$exists": True}}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$key",
                    "search_type": {"$first": "$search_type"},
                    "params": {"$first": "$params"},
                    "results_count": {"$first": "$results_count"},
                    "timestamp": {"$first": "$timestamp"},
                }
            },
            {"$sort": {"timestamp": -1}},
            {"$limit": 5},
        ]

        # for r in col.aggregate(pipeline):
        #     print(f"{r['search_type']} | {r['params']} | rows={r['results_count']} | {r['timestamp']}")

        return list(col.aggregate(pipeline))

    except Exception as e:
        print(f"[ERROR] MongoDB stats failed: {e}")
        print("Tip: check MongoDB is running and mongo_config is correct.")



if __name__ == "__main__":
    print(len(stats_top5_frequency()))
    for r in stats_top5_frequency():
        print(r["count"], r["search_type"], r["params"], r["results_count"], r["timestamp"])
    # col = get_mongo_collection()
    # print(col.count_documents({}))
    #
    # print(stats_top5_frequency())
