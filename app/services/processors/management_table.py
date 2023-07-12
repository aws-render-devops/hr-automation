from pprint import pprint
from app.services.sql import (
    get_pipeline_counts,
    get_latest_vacancy_status_changes,
    get_all_vacancy_status_changes,
    get_hired_status_update_date,
    get_all_vacancies,
    get_all_employees,
    get_all_collaborators,
    get_vacancies_hired_candidates_fusion,
)
from collections import defaultdict
from app.models import Employee, Vacancy
from app.consts import VacancyStatus
import pandas as pd


async def collect_time_to_hire() -> dict:
    result = await get_pipeline_counts()
    counts_map = defaultdict(dict)
    for record in result:
        counts_map[record['vacancy_id']][record['name']] = record['count']
    return counts_map


async def get_vacancies_latest_status_changes():
    result = await get_latest_vacancy_status_changes()
    status_map = {}
    for record in result:
        status_map[record['vacancy_id']] = {
            'new': record['status_new'],
            'created_at': record['created_at'],
            'old': record['status_old'],
        }
    return status_map


async def get_all_vacancies_status_changes():
    result = await get_all_vacancy_status_changes()
    status_map = defaultdict(list)
    for record in result:
        status_map[record['vacancy_id']].append(
            {
                'new': record['status_new'],
                'old': record['status_old'],
                'created_at': record['created_at'],
            }
        )


async def get_vacancies_hired_date():
    result = await get_hired_status_update_date()
    hired_map = {}
    for record in result:
        hired_map[record['vacancy_id']] = {
            'updated_at': record['updated_at'],
            'name': record['name'],
        }
    return hired_map


async def get_employees():
    result = await get_all_employees()
    employees_objects = [Employee.parse_obj(dict(item)) for item in result]
    return {item.id: item for item in employees_objects}


async def get_collaborators():
    result = await get_all_collaborators()
    collaborators_map = defaultdict(list)
    for item in result:
        collaborators_map[item['vacancy_id']].append(
            Employee.parse_obj(
                {
                    'id': item['employee_id'],
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                }
            )
        )
    return collaborators_map


async def get_hired_names_vacancy_map():
    result = await get_vacancies_hired_candidates_fusion()
    return {item['id']: item['full_name'] for item in result}


async def prepare_vacancies():
    employees_map = await get_employees()
    collaborators_map = await get_collaborators()
    vacancies = await get_all_vacancies()
    vacancies_objects = [Vacancy.parse_obj(dict(item)) for item in vacancies]
    latest_status_changes = await get_vacancies_latest_status_changes()
    all_vacancies_status_changes = await get_vacancies_latest_status_changes()
    close_transition_map = {
        key: value for key, value in all_vacancies_status_changes.items() if value['new'] == VacancyStatus.CLOSED
    }
    time_to_hire_map = await collect_time_to_hire()
    # hired_dates = await get_vacancies_hired_date()
    hired_names = await get_hired_names_vacancy_map()
    vacancies_hired_dates = await get_vacancies_hired_date()
    result = []

    for vacancy in vacancies_objects:
        prepared_vac = {
            'id': vacancy.id,
            'recruiter': employees_map[vacancy.recruiter],
            'title': vacancy.title,
            'seniority': vacancy.seniority,
            'status': vacancy.status,
            'opened_at': vacancy.opened_at,
            'created_at': vacancy.created_at,
            'collaborators': collaborators_map.get(vacancy.id),
            'full_name': hired_names.get(vacancy.id),
        }
        current_vacancy_old_status = latest_status_changes.get(vacancy.id, {}).get('status_old', None)
        if vacancy.status == VacancyStatus.CLOSED or (
                current_vacancy_old_status is not None and
                current_vacancy_old_status == VacancyStatus.CLOSED
        ):
            prepared_vac['closed_by'] = prepared_vac['recruiter']
        if (
                vacancy.status in (VacancyStatus.CANCELLED, VacancyStatus.CLOSED, VacancyStatus.ARCHIVED) and
                vacancy.opened_at is not None
        ):
            prepared_vac['days_in_operation'] = (
                    latest_status_changes.get(vacancy.id, {}).get('created_at', vacancy.updated_at) - vacancy.opened_at
            ).days
        if vacancy.id in vacancies_hired_dates:
            prepared_vac['time_to_hire'] = (
                    vacancies_hired_dates[vacancy.id]['updated_at'] - vacancy.opened_at
            ).days
        if (
                (
                    vacancy.status == VacancyStatus.CLOSED or
                    vacancy.id in close_transition_map)
                and vacancy.opened_at is not None
        ):
            closing_date = close_transition_map.get(vacancy.id, {}).get('created_at', vacancy.updated_at)
            prepared_vac['time_to_fill'] = (closing_date - vacancy.opened_at).days
        if 'time_to_fill' in prepared_vac and 'time_to_hire' in prepared_vac:
            prepared_vac['waiting_time'] = prepared_vac['time_to_fill'] - prepared_vac['time_to_hire']
        if vacancy.id in time_to_hire_map:
            prepared_vac['time_to_hire_hr'] = time_to_hire_map[vacancy.id].get('Интервью с HR', 0)
            prepared_vac['time_to_hire_technical'] = time_to_hire_map[vacancy.id].get('Техническое интервью', 0)
        result.append(prepared_vac)
    return result


def sort_management_result_by_year_and_quarter(vacanies: list):
    data = {
        'Id': list(),
        'Recruiter': list(),
        'Title': list(),
        'Seniority': list(),
        'Status': list(),
        'Opened at': list(),
        'Closed by': list(),
        'Days in operation': list(),
        'Time to fill': list(),
        'Time to hire': list(),
        'Waiting time': list(),
        'Full name': list(),
        'Time to hire HR': list(),
        'Time to hire technical': list(),
        'Collaborators': list(),
        'Created at': list(),
    }
    for vacancy in vacanies:

        data['Id'].append(vacancy['id'])
        data['Recruiter'].append(vacancy['recruiter'])
        data['Title'].append(vacancy['title'])
        data['Seniority'].append(vacancy.get('seniority'))
        data['Status'].append(vacancy['status'])
        data['Opened at'].append(vacancy.get('opened_at'))
        data['Closed by'].append(vacancy.get('closed_by'))
        data['Days in operation'].append(vacancy.get('days_in_operation'))
        data['Time to fill'].append(vacancy.get('time_to_fill'))
        data['Time to hire'].append(vacancy.get('time_to_hire'))
        data['Waiting time'].append(vacancy.get('waiting_time'))
        data['Full name'].append(vacancy.get('full_name'))
        data['Time to hire HR'].append(vacancy.get('time_to_hire_hr', 0))
        data['Time to hire technical'].append(vacancy.get('time_to_hire_technical', 0))
        data['Collaborators'].append(vacancy['collaborators'])
        data['Created at'].append(vacancy['created_at'])
    df = pd.DataFrame(data)
    df['Year'] = df['Created at'].dt.year
    df['Quarter'] = df['Created at'].dt.quarter
    df = df.sort_values(by=['Year', 'Quarter']).reset_index(drop=True)
    return df

