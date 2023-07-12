from datetime import datetime
import pydantic


class PipelineState(pydantic.BaseModel):
    id: int
    pf_id: int
    name: str
    created_at: datetime
    application: int

    class Config:
        allow_population_by_field_name = True
        fields = {
            'application': 'application_id',
        }
