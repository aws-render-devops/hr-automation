from settings import settings
from app.services.utils import pull_all_data_from_source, get_storage_object
from datetime import datetime
from app.logger import Logged


PF_HEADERS = {"X-API-KEY": settings.pf_api_key, "accept": "application/json"}


@Logged
async def get_all_vacancies() -> list:
    return await pull_all_data_from_source(
        url=settings.pf_all_vacancies_url,
        headers=PF_HEADERS,
    )


@Logged
async def get_all_candidates() -> list:
    return await pull_all_data_from_source(
        url=settings.pf_all_candidates_url,
        headers=PF_HEADERS,
    )


@Logged
async def get_vacancy_candidates(vacancy_id: int) -> list:
    return await pull_all_data_from_source(
        url=settings.pf_vacancy_candidates_url.format(vacancy_id=vacancy_id),
        headers=PF_HEADERS,
    )


@Logged
async def get_vacancy_applications(vacancy_id: int) -> list:
    return await pull_all_data_from_source(
        url=settings.pf_applications_url.format(vacancy_id=vacancy_id),
        headers=PF_HEADERS,
    )


@Logged
def get_all_employees_from_vacancies(vacancies: list) -> dict:
    employees = {}
    for vacancy in vacancies:
        hr_lead = vacancy['hiring_lead']
        employees[hr_lead['id']] = {
            'first_name': hr_lead['first_name'],
            'last_name': hr_lead['last_name'],
            'email': hr_lead['email'],
        }
        collaborators = vacancy['collaborators']
        for collaborator in collaborators:
            employees[collaborator['id']] = {
                'first_name': collaborator['first_name'],
                'last_name': collaborator['last_name'],
                'email': collaborator['email'],
            }
    return employees


@Logged
async def process_vacancies(vacancies: list, storage: dict | None = None):

    if storage is None:
        storage = get_storage_object()

    for vacancy in vacancies:

        await prepare_single_vacancy(vacancy, storage)

    # prepare_candidates(storage)

    return storage


@Logged
def prepare_single_pipeline_state(state: dict, application_id: int, storage: dict) -> dict:
    storage['pipeline_states'].append({
        'pf_id': state['id'],
        'name': state['name'],
        'application_id': application_id,
    })


@Logged
async def prepare_single_application(application: dict, vacancy_id: int, storage: dict | None = None, skip_state=False):
    if storage is None:
        storage = get_storage_object()

    if application.get('pipeline_state') is not None and not skip_state:
        state = application['pipeline_state']
        prepare_single_pipeline_state(state, application['id'], storage)
    candidate = {
        'candidate_full_name': None,
        'candidate_id': None,
        'candidate_email': None,
        'candidate_source': None,
    }
    if application.get('applicant') is not None and application['applicant']['id'] in storage['_candidates']:
        applicant = storage['_candidates'][application['applicant']['id']]
        candidate = {
            'candidate_full_name': applicant['full_name'],
            'candidate_id': applicant['id'],
            'candidate_email': applicant['email'],
            'candidate_source': applicant['source'],
        }
    storage['applications'].append({
        'id': application['id'],
        'vacancy_id': vacancy_id,
        'disqualified_at': datetime.strptime(application['disqualified_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if application.get('disqualified_at') else None,
        'created_at': datetime.strptime(application['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        'updated_at': datetime.strptime(application['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        'disqualify_reason': application['disqualify_reason']['name']
        if application.get('disqualify_reason') else None,  # noqa
        **candidate,
    })
    return storage


@Logged
async def prepare_single_vacancy(vacancy: dict, storage: dict | None = None):
    if storage is None:
        storage = get_storage_object()

    candidates = await get_vacancy_candidates(vacancy['id'])
    candidates_map = {candidate['id']: candidate for candidate in candidates}
    storage['_candidates'] |= candidates_map

    storage['employees'] |= get_all_employees_from_vacancies([vacancy])
    applications = await get_vacancy_applications(vacancy['id'])
    tmp_vac = {
        'id': vacancy['id'],
        'recruiter_id': vacancy['hiring_lead']['id'],
        'title': vacancy['title'],
        'status': vacancy['state'],
        'opened_at': datetime.strptime(vacancy['opened_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if vacancy['opened_at'] else None,
        'interviews_to_hire_hr': 0,
        'interviews_to_hire_tech': 0,
        'created_at': datetime.strptime(vacancy['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        'updated_at': datetime.strptime(vacancy['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
    }
    if tmp_vac['status'] in {'cancelled', 'archived', 'held'} and vacancy['opened_at'] is not None:
        tmp_vac['days_in_operation'] = (
                datetime.strptime(vacancy['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ') -
                datetime.strptime(vacancy['opened_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        ).days
    if tmp_vac['status'] in {'closed', 'archived'}:
        if vacancy['opened_at'] is not None and vacancy.get('closed_at') is not None:
            tmp_vac['time_to_fill'] = (
                    datetime.strptime(vacancy['closed_at'], '%Y-%m-%dT%H:%M:%S.%fZ') -
                    datetime.strptime(vacancy['opened_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ).days
        tmp_vac['seniority'] = vacancy['applicant_level']['name'] if vacancy['applicant_level'] else None
    pipeline_states = []
    for application in applications:
        await prepare_single_application(application, vacancy['id'], storage)
    if tmp_vac.get('time_to_fill') and tmp_vac.get('time_to_hire'):
        tmp_vac['waiting_time'] = tmp_vac['time_to_fill'] - tmp_vac['time_to_hire']
    for collaborator in vacancy['collaborators']:
        storage['collaborators'].append({
            'employee_id': collaborator['id'],
            'vacancy_id': vacancy['id'],
        })
    storage['pipeline_states'].extend(pipeline_states)
    storage['vacancies'].append(tmp_vac)

    return storage
