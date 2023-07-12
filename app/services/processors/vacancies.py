from datetime import datetime
from app.logger import Logged

from app.consts import VacancyStatus
from app.models import Vacancy, Application, PipelineState
from app.services.people_force import (
    get_vacancy_applications,
    prepare_single_application,
    prepare_single_pipeline_state,
    get_vacancy_candidates,
)
from app.services.people_force import prepare_single_vacancy
from app.services.sql import (
    upsert_vacancies_from_storage,
    create_vacancy_status_history_event,
    update_vacancy as update_vacancy_sql,
    get_all_applications_for_vacancy,
    get_latest_pipeline_states,
)
from app.services.utils import get_storage_object


async def update_vacancy(vacancy: dict):
    data = {
        'title': vacancy['title'],
        'status': vacancy['state'],
        'updated_at': datetime.strptime(vacancy['updated_at'],'%Y-%m-%dT%H:%M:%S.%fZ'),
        'id': vacancy['id'],
        'seniority': None,
    }

    if vacancy['state'] == VacancyStatus.CLOSED:
        data['seniority'] = vacancy['applicant_level']['name'] if vacancy['applicant_level'] else None
    await update_vacancy_sql(data)


@Logged
async def process_vacancy_update(pf_vacancy: dict, db_vacancy: Vacancy | None):
    storage = get_storage_object()
    if db_vacancy is None:
        storage = await prepare_single_vacancy(pf_vacancy, storage=storage)
        await upsert_vacancies_from_storage(storage)
        return
    if pf_vacancy['state'] == db_vacancy.status and pf_vacancy in [
                                                                        VacancyStatus.CLOSED,
                                                                        VacancyStatus.CANCELLED,
                                                                        VacancyStatus.ARCHIVED
    ]:
        return
    if pf_vacancy['state'] != db_vacancy.status:
        await create_vacancy_status_history_event(db_vacancy.id, db_vacancy.status, pf_vacancy['state'])
        await update_vacancy(pf_vacancy)

    candidates = await get_vacancy_candidates(pf_vacancy['id'])
    candidates_map = {candidate['id']: candidate for candidate in candidates}
    storage['_candidates'] |= candidates_map

    applications_db = await get_all_applications_for_vacancy(db_vacancy.id)
    applications_objects = [Application.parse_obj(dict(application)) for application in applications_db]
    applications_map = {application.id: application for application in applications_objects}
    applications_pf = await get_vacancy_applications(db_vacancy.id)
    applications_to_be_created = []
    applications_to_be_updated = []

    for application in applications_pf:
        if not application['id'] in applications_map:
            applications_to_be_created.append(application)
        else:
            applications_to_be_updated.append(application)
    storage = get_storage_object()
    for application in applications_to_be_created:
        await prepare_single_application(application, vacancy_id=db_vacancy.id, storage=storage)

    db_states = await get_latest_pipeline_states()
    if db_states is not None:
        states_objects = [PipelineState.parse_obj(dict(state)) for state in db_states]
        pipeline_status_map = {state.application: state for state in states_objects}
    for application in applications_to_be_updated:

        if (
                application.get('disqualified_at') is not None and
                datetime.strptime(application['disqualified_at'], '%Y-%m-%dT%H:%M:%S.%fZ') !=
                applications_map[application['id']].disqualified_at
        ):
            await prepare_single_application(application, vacancy_id=db_vacancy.id, storage=storage, skip_state=True)
        if (
                db_states is not None and
                application.get('pipeline_state') is not None and
                application['pipeline_state']['name'] != pipeline_status_map[application['id']].name
        ):
            prepare_single_pipeline_state(application['pipeline_state'], application['id'], storage)
    await upsert_vacancies_from_storage(storage)

