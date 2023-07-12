import aiohttp
from settings import settings
import asyncpg
from functools import wraps


class Highlander:

    def __init__(self, cls):
        self._cls = cls
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance


async def pull_all_data_from_source(url: str, headers: dict, params: dict = None):
    params = params if params is not None else {}
    result = []
    page = 1
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(
                    url,
                    headers=headers,
                    params=params
            ) as resp:
                if resp.status != 200:
                    # !TODO Process error here
                    break
                resp = await resp.json()
                if resp['metadata']['pagination']['pages'] >= page:
                    result.extend(resp['data'])
                    page += 1
                    params.update({"page": page})
                else:
                    break
    return result


def get_storage_object():
    # Order does matter here because of foreign keys
    return {
        'employees': {},
        'vacancies': [],
        'applications': [],
        'candidates': [],
        'pipeline_states': [],
        'collaborators': [],
        'applicants': [],
        '_candidates': {},
    }
