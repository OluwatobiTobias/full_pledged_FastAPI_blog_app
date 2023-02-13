import datetime
import json
from typing import Any, Dict, Union

from fastapi import Request

from fastapi_blog import INIT_DATA_PATH
from fastapi_blog.models import database, post_tags, posts, tags


def parse_date(date_str):
    try:
        return datetime.datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.datetime.now()


def datetime_parser(dct: Dict[Union[str, int], Any]) -> Dict[Union[str, int], Any]:
    for key, val in dct.items():
        if isinstance(val, dict):
            dct[key] = datetime_parser(val)
        elif key in ["date", "datetime"]:
            dct[key] = parse_date(val)
    return dct


async def init_db():
    "func `init_db` loads db with data from config/initial_data.json"
    with open(INIT_DATA_PATH) as f:
        init_data = json.load(f, object_hook=datetime_parser)
    table_by_name = {"posts": posts, "tags": tags, "post_tags": post_tags}
    for table_name, inserts in init_data.items():
        table = table_by_name[table_name]
        query = table.insert().values(inserts)
        await database.execute(query)


async def teardown_db():
    "funcs `teardown_db` deals all rows of model tables [posts, tags, post_tags] in db"
    for table in [posts, tags, post_tags]:
        query = table.delete()
        await database.execute(query)


def get_context(request: Request, **kwargs) -> Dict[str, Any]:
    "func `get_context` returns FastAPI.Request and **kwargs in dict"
    context = {"request": request, **kwargs}
    return context
