import pydantic


class Employee(pydantic.BaseModel):
    id: int
    first_name: str
    last_name: str
