from .management_table import prepare_vacancies
from app.services.sql import get_pipeline_name_for_vacancy
from datetime import datetime, time


async def prepare_acceptance_rate():
    vacancies = await prepare_vacancies()
    aimed_vacancies = [vacancy for vacancy in vacancies if vacancy.get('seniority') is not None]
    seniority_map = {vacancy['id']: vacancy['seniority'] for vacancy in aimed_vacancies}
    today = datetime.now().date()
    quarter_start_month = (today.month - 1) // 3 * 3 + 1
    quarter_start_date = today.replace(month=quarter_start_month, day=1)
    start_date = datetime.combine(quarter_start_date, time.min)
    hired = await get_pipeline_name_for_vacancy('Нанят', start_date=start_date)
    offered = await get_pipeline_name_for_vacancy('Выставлен оффер', start_date=start_date)
    result = {
        'Junior': {'accepted': 0, 'offered': 0},
        'Middle': {'accepted': 0, 'offered': 0},
        'Senior': {'accepted': 0, 'offered': 0},
    }
    for item in hired:
        if item['vacancy_id'] not in seniority_map:
            continue
        result[seniority_map[item['vacancy_id']]]['accepted'] += 1
        result[seniority_map[item['vacancy_id']]]['offered'] += 1

    for item in offered:
        result[seniority_map[item['vacancy_id']]]['offered'] += 1

    for key in result.keys():
        result[key]['rate'] = result[key]['accepted'] / result[key]['offered'] * 100
    return result
