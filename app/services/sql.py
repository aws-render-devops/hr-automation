import asyncpg
from settings import settings
from collections.abc import Iterable
from datetime import datetime


_pool = None


async def _get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            f'postgresql://{settings.db_user}:{settings.db_pwd}'
            f'@{settings.db_host}:{settings.db_port}/{settings.db_name}'
        )
    return _pool


async def execute_values(stm: str, values: list):
    pool = await _get_pool()
    conn = await pool.acquire()
    batches = [values[i:i + 1000] for i in range(0, len(values), 1000)]
    try:
        for batch in batches:
            await conn.executemany(stm, batch)
    except Exception as e:
        print(stm)
        print(e)
        # !TODO process exception
    finally:
        await pool.release(conn)


async def get_values(stm: str, *args):
    pool = await _get_pool()
    conn = await pool.acquire()
    try:
        return await conn.fetch(stm, *args)
    except Exception as e:
        ...
    finally:
        await pool.release(conn)


async def insert_employees(employees: dict):
    stm = """
            INSERT INTO employees (
                id, first_name, last_name
            ) VALUES ($1, $2, $3)
           ON CONFLICT(id) DO NOTHING;
       """
    await execute_values(stm, [(key, value['first_name'], value['last_name']) for key, value in employees.items()])


async def insert_candidates(candidates: list):

    stm = """
            INSERT INTO candidates (
                id, full_name, email, application_id, source
            ) VALUES ($1, $2, $3, $4, $5)
           ON CONFLICT(id) DO NOTHING;
       """
    await execute_values(
        stm,
        [
            (
                candidate['id'],
                candidate['full_name'],
                candidate['email'],
                candidate['source'],
            ) for candidate in candidates
        ]
    )


async def insert_pipeline_states(states: list):

    stm = """
            INSERT INTO pipeline_states (
                pf_id, name, application_id
            ) VALUES ($1, $2, $3)
           ON CONFLICT(id) DO UPDATE
           SET name = EXCLUDED.name, 
           pf_id = EXCLUDED.pf_id;
       """

    await execute_values(
        stm,
        [
            (
                state['pf_id'],
                state['name'],
                state['application_id'],
            ) for state in states
        ]
    )


async def insert_vacancies(vacancies: list):

    default_values = {
        'time_to_fill': None,
        'time_to_hire': None,
        'waiting_time': None,
        'closed_by': None,
        'days_in_operation': None,
        'seniority': None,
        'full_name': None,
    }

    stm = """
            INSERT INTO vacancies (
                id, title, status, opened_at, created_at, updated_at, recruiter_id, 
                closed_by_id, seniority, full_name, time_to_fill, 
                time_to_hire, waiting_time, days_in_operation, interviews_to_hire_hr, interviews_to_hire_tech
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
           ON CONFLICT(id) DO UPDATE
           SET status = EXCLUDED.status,
            opened_at = EXCLUDED.opened_at,
            closed_by_id = EXCLUDED.closed_by_id,
            seniority = EXCLUDED.seniority,
            full_name = EXCLUDED.full_name;
       """

    results = []
    for vacancy in vacancies:
        results.append({**default_values, **vacancy})

    await execute_values(
        stm,
        [
            (
                vacancy['id'],
                vacancy['title'],
                vacancy['status'],
                vacancy['opened_at'],
                vacancy['created_at'],
                vacancy['updated_at'],
                vacancy['recruiter_id'],
                vacancy['closed_by'],
                vacancy['seniority'],
                vacancy['full_name'],
                vacancy['time_to_fill'],
                vacancy['time_to_hire'],
                vacancy['waiting_time'],
                vacancy['days_in_operation'],
                vacancy['interviews_to_hire_hr'],
                vacancy['interviews_to_hire_tech'],
            ) for vacancy in results
        ]
    )


async def insert_applications(applications: list):

    stm = """
            INSERT INTO applications (
                id, vacancy_id, created_at, 
                updated_at, disqualified_at, disqualify_reason,
                candidate_source, candidate_id, candidate_email, 
                candidate_full_name
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
           ON CONFLICT(id) DO UPDATE 
           SET disqualified_at = EXCLUDED.disqualified_at,
            disqualify_reason = EXCLUDED.disqualify_reason,
            updated_at = EXCLUDED.updated_at;
       """

    await execute_values(
        stm,
        [
            (
                application['id'],
                application['vacancy_id'],
                application['created_at'],
                application['updated_at'],
                application['disqualified_at'],
                application['disqualify_reason'],
                application['candidate_source'],
                application['candidate_id'],
                application['candidate_email'],
                application['candidate_full_name'],
            ) for application in applications
        ]
    )


async def insert_applicants(applicants: list):

    stm = """
            INSERT INTO applicants (
                application_id, candidate_id
            ) VALUES ($1, $2)
           ON CONFLICT DO NOTHING;
       """

    await execute_values(
        stm,
        [
            (
                applicant['application_id'],
                applicant['candidate_id'],
            ) for applicant in applicants
        ]
    )


async def insert_collaborators(collaborators: list):
    pool = await _get_pool()
    conn = await pool.acquire()
    stm = """
            INSERT INTO collaborators (
                employee_id, vacancy_id
            ) VALUES ($1, $2)
            ON CONFLICT DO NOTHING
       """

    try:
        await conn.executemany(
            stm,
            [
                (
                    collaborator['employee_id'],
                    collaborator['vacancy_id'],
                ) for collaborator in collaborators
            ]
        )
    finally:
        await pool.release(conn)


async def get_all_applications_for_vacancy(vacancy_id: int):
    stm = """
            SELECT id, vacancy_id, created_at, updated_at, disqualified_at, disqualify_reason 
            FROM applications WHERE vacancy_id = $1;
       """
    return await get_values(stm, vacancy_id)


async def get_all_pipeline_states_for_applications(application_ids: Iterable):
    stm = """
            SELECT pf_id, name, created_at, application_id 
            FROM pipeline_states WHERE application_id = ANY($1);
       """
    return await get_values(stm, application_ids)


async def get_all_not_closed_vacancies():
    stm = """
            SELECT id, recruiter_id, title, status, opened_at, closed_by_id, created_at,
            seniority, interviews_to_hire_hr, interviews_to_hire_tech, full_name
            FROM vacancies WHERE status != 'closed';
       """
    return await get_values(stm)


async def get_all_vacancies():
    stm = """
            SELECT id, recruiter_id, title, status, opened_at, updated_at, closed_by_id, created_at,
            seniority, interviews_to_hire_hr, interviews_to_hire_tech, full_name
            FROM vacancies;
       """
    return await get_values(stm)


async def create_vacancy_status_history_event(vacancy_id: int, status_old: str, status_new):
    stm = """
            INSERT INTO vacancy_status_history (
                vacancy_id, status_old, status_new
            ) VALUES ($1, $2, $3);
       """
    await execute_values(stm, [(vacancy_id, status_old, status_new)])


async def update_vacancy(vacancy: dict):
    stm = """
            UPDATE vacancies SET
                status = $1, updated_at = $2, title = $3, seniority = $4
            WHERE id = $5;
    """
    await execute_values(
        stm,
        [
            [
                vacancy['status'],
                vacancy['updated_at'],
                vacancy['title'],
                vacancy['seniority'],
                vacancy['id']
            ]
        ]
    )


async def get_latest_pipeline_states():
    stm = """
            SELECT DISTINCT ON (application_id) id, pf_id, name, created_at, application_id 
            FROM pipeline_states ORDER BY application_id, created_at DESC;
       """
    return await get_values(stm)


async def upsert_vacancies_from_storage(store: dict):

    upsertion_map = {
        'employees': insert_employees,
        'vacancies': insert_vacancies,
        'applications': insert_applications,
        'pipeline_states': insert_pipeline_states,
        # 'candidates': insert_candidates,
        'collaborators': insert_collaborators,
        # 'applicants': insert_applicants,
    }
    for key, value in store.items():
        if key not in upsertion_map:
            continue
        await upsertion_map[key](value)


async def get_pipeline_counts():
    stm = """
        SELECT applications.vacancy_id, name, COUNT(name)
        FROM pipeline_states JOIN applications
            ON pipeline_states.application_id = applications.id
        GROUP BY name, applications.vacancy_id;
    """
    return await get_values(stm)


async def get_latest_vacancy_status_changes():
    stm = """
        SELECT DISTINCT ON (vacancy_id) vacancy_id, created_at, status_new, status_old
        FROM vacancy_status_history 
        ORDER BY vacancy_id, created_at DESC;
    """
    return await get_values(stm)


async def get_all_vacancy_status_changes():
    stm = """
        SELECT vacancy_id, created_at, status_new, status_old 
        FROM vacancy_status_history ;
    """
    return await get_values(stm)


async def get_hired_status_update_date():
    stm = """
        select applications.vacancy_id, applications.updated_at, name
        from pipeline_states join applications
            on pipeline_states.application_id = applications.id
        where name = 'Нанят';
    """
    return await get_values(stm)


async def get_all_employees():
    stm = """
        SELECT * FROM employees;
    """
    return await get_values(stm)


async def get_all_collaborators():
    stm = """
        SELECT 
            collaborators.vacancy_id, 
            collaborators.employee_id, 
            employees.first_name, 
            employees.last_name
        FROM collaborators JOIN employees ON collaborators.employee_id = employees.id;    
    """
    return await get_values(stm)


async def get_vacancies_hired_candidates_fusion():
    stm = """
        SELECT vacancies.id, applications.candidate_full_name as full_name
        FROM applications
        JOIN pipeline_states ON applications.id = pipeline_states.application_id
        JOIN vacancies ON applications.vacancy_id = vacancies.id
        WHERE pipeline_states.name = 'Нанят';
    """
    return await get_values(stm)


async def get_applications_from_date(date_start, date_end):
    stm = """
        SELECT * 
        FROM applications 
        WHERE created_at >= $1
        AND created_at < $2
        ORDER BY created_at ASC;
    """
    return await get_values(stm, date_start, date_end)


async def get_disqualified_applications_from_date(date_start, date_end):
    stm = """
        SELECT * 
        FROM applications 
        WHERE disqualified_at >= $1
        AND disqualified_at < $2
        ORDER BY disqualified_at ASC;
    """
    return await get_values(stm, date_start, date_end)


async def get_pipeline_name_for_vacancy(pipeline_stat: str, start_date: datetime):
    stm = """
        SELECT pipeline_states.name, pipeline_states.application_id, a.vacancy_id
        FROM pipeline_states
        JOIN applications a ON pipeline_states.application_id = a.id
        JOIN vacancies v ON v.id = a.vacancy_id
        WHERE name = $1
        AND pipeline_states.created_at >= $2;
    """
    return await get_values(stm, pipeline_stat, start_date)
