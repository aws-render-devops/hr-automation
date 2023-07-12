from datetime import datetime
import pydantic


class Application(pydantic.BaseModel):
    id: int
    vacancy: int
    created_at: datetime
    updated_at: datetime
    disqualified_at: datetime | None = None
    disqualify_reason: str | None = None
    candidate_id: int | None = None
    candidate_email: str | None = None
    candidate_source: str | None = None
    candidate_full_name: str | None = None

    class Config:
        allow_population_by_field_name = True
        fields = {
            'vacancy': 'vacancy_id',
        }
