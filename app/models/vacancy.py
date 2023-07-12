from datetime import datetime
import pydantic


class Vacancy(pydantic.BaseModel):
    id: int
    recruiter: int
    title: str
    status: str
    opened_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    closed_by: int | None = None
    seniority: str | None = None
    interviews_to_hire_hr: int | None = None
    interviews_to_hire_tech: int | None = None
    full_name: str | None = None

    class Config:
        allow_population_by_field_name = True
        fields = {
            'recruiter': 'recruiter_id',
            'closed_by': 'closed_by_id',
        }
