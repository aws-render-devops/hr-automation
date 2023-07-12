import asyncio
from functools import wraps

from app.models import Vacancy
from app.services.sql import get_all_vacancies as db_get_all_vacancies
from app.services.people_force import (
    get_all_vacancies as pf_get_all_vacancies,
    get_all_candidates as pf_get_all_candidates,
)
from app.services.people_force import process_vacancies
from app.services.sql import (
    upsert_vacancies_from_storage,
)
from app.services.processors.vacancies import process_vacancy_update
from app.services.utils import get_storage_object


def wrap_task(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            await coro(*args, **kwargs)
        except Exception as e:
            print(e)
            # Todo: process exception
    return wrapper


async def create_vacancies():  # Not used?

    storage = await process_vacancies(await pf_get_all_vacancies())
    await upsert_vacancies_from_storage(storage)


async def vacancy_task():
    print('vacancy task started!')
    vacancies = await db_get_all_vacancies()
    db_vacancies = [Vacancy.parse_obj(dict(vacancy)) for vacancy in vacancies]
    pf_vacancies = await pf_get_all_vacancies()
    db_vacancies_map = {vacancy.id: vacancy for vacancy in db_vacancies}
    batches = [pf_vacancies[i:i + 10] for i in range(0, len(pf_vacancies), 10)]
    for batch in batches:
        await asyncio.gather(
            *[
                wrap_task(process_vacancy_update)(vacancy, db_vacancies_map.get(vacancy['id'])) for vacancy in batch
            ]
        )
        # for vacancy in batch:
        #     await process_vacancy_update(vacancy, db_vacancies_map.get(vacancy['id']))


async def initial_task():
    vacancies = await pf_get_all_vacancies()
    # candidates = await pf_get_all_candidates()
    storage = get_storage_object()
    # storage['_candidates'] = candidates
    storage = await process_vacancies(vacancies, storage=storage)
    await upsert_vacancies_from_storage(storage)

