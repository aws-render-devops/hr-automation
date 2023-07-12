create table employees (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(40),
    last_name VARCHAR(40)
);

create table vacancies (
    id INTEGER PRIMARY KEY,
    recruiter_id INTEGER NOT NULL REFERENCES employees(id),
    title VARCHAR(100) NOT NULL,
    status varchar(50) NOT NULL ,
    opened_at timestamp NULL,
    created_at timestamp,
    updated_at timestamp,
    closed_by_id INTEGER NULL REFERENCES employees(id),
    seniority VARCHAR(20) NULL ,
    interviews_to_hire_hr INTEGER NULL ,
    interviews_to_hire_tech INTEGER NULL,
    full_name VARCHAR(80) NULL,
    days_in_operation INTEGER NULL,
    time_to_hire INTEGER NULL,
    time_to_fill INTEGER NULL,
    waiting_time INTEGER NULL
);


CREATE TABLE collaborators (
    employee_id INTEGER REFERENCES employees(id),
    vacancy_id INTEGER REFERENCES vacancies(id),
    UNIQUE (employee_id, vacancy_id)
);

CREATE TABLE applications (
    id INTEGER PRIMARY KEY ,
    vacancy_id INTEGER REFERENCES vacancies(id),
    disqualified_at timestamp NULL ,
    created_at timestamp,
    updated_at timestamp,
    disqualify_reason VARCHAR(100) NULL,
    candidate_full_name VARCHAR(80) NULL,
    candidate_source VARCHAR(80) NULL,
    candidate_id INTEGER NULL,
    candidate_email VARCHAR(80) NULL
);


CREATE TABLE candidates (
    id INTEGER PRIMARY KEY ,
    full_name varchar(80) ,
    email VARCHAR(80) NULL,
    source VARCHAR(80) NULL
);


CREATE TABLE applicants (
                            candidate_id INTEGER REFERENCES candidates(id),
                            application_id INTEGER REFERENCES applications(id),
                            UNIQUE (candidate_id, application_id)
);


CREATE TABLE pipeline_states (
    id SERIAL PRIMARY KEY,
    pf_id INTEGER,
    name VARCHAR(80),
    application_id INTEGER REFERENCES applications(id),
    created_at timestamp DEFAULT now()
);


CREATE TABLE vacancy_status_history(
    id SERIAL PRIMARY KEY,
    vacancy_id INTEGER REFERENCES vacancies(id),
    status_old VARCHAR(50),
    status_new VARCHAR(50),
    created_at timestamp DEFAULT now()
);



grant all privileges on table employees to hrscript;
grant all privileges on table vacancies to hrscript;
grant all privileges on table collaborators to hrscript;
grant all privileges on table candidates to hrscript;
grant all privileges on table applications to hrscript;
grant all privileges on table pipeline_states to hrscript;
grant all privileges on table pipeline_states_id_seq to hrscript;
grant all privileges on table vacancy_status_history to hrscript;
grant all privileges on table vacancy_status_history_id_seq to hrscript;
grant all privileges on table applicants to hrscript;