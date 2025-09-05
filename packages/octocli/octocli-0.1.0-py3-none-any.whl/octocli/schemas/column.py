from pydantic import BaseModel


class ColumnSchema(BaseModel):
    name: str
    type_: str
    sql_type: str
