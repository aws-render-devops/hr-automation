from datetime import datetime, date, time, timedelta
from app.services.sql import get_disqualified_applications_from_date, get_all_vacancies
from app.models import Application, Vacancy
from collections import defaultdict


async def process_disqualified():

    dt_end = datetime.combine(date.today(), time.min)
    dt_start = dt_end - timedelta(days=28)
    applications = await get_disqualified_applications_from_date(date_start=dt_start, date_end=dt_end)
    application_objects = [Application.parse_obj(dict(application)) for application in applications]
    vacancies = await get_all_vacancies()
    vacancy_objects = [Vacancy.parse_obj(dict(vacancy)) for vacancy in vacancies]
    vacancies_map = {vacancy.id: vacancy for vacancy in vacancy_objects}
    result = {}

    if not application_objects:
        raise Exception('No applications found')
    first_week = application_objects[0].disqualified_at.isocalendar()[1]
    for application in application_objects:
        tmp = result.get(application.disqualified_at.isocalendar()[1] - first_week, defaultdict(list))
        sub_dict = tmp.get(application.vacancy, {})
        if application.disqualify_reason is None:
            continue
        sub_dict[application.disqualify_reason] = sub_dict.get(
            application.disqualify_reason, 0
        ) + 1
        sub_dict['_applications'] = sub_dict.get('_applications', []) + [application]
        tmp[application.vacancy] = sub_dict
        result[application.disqualified_at.isocalendar()[1] - first_week] = tmp
    result['_vacancies'] = vacancies_map
    return result
