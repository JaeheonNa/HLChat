import json
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


def get_secret(
    key: str,
    default_value: Optional[str] = None,
    json_path: str = str(BASE_DIR / "secrets.json"),
):
    with open(json_path) as json_file:
        secrets = json.load(json_file)
    try:
        # dot notation 파싱
        keys = key.split(".")
        value = secrets
        for k in keys:
            value = value[k]
        return value
    except KeyError:
        if default_value:
            return default_value
        raise EnvironmentError(f"Set the {key} environment variable.")


redis_host = get_secret("redis.host")
redis_port = get_secret("redis.port")
redis_db = get_secret("redis.db")

mysql_url = get_secret("mysql_url")

mongo_host = get_secret("mongo.host")
mongo_port = get_secret("mongo.port")
mongo_db_name = get_secret("mongo.db")
