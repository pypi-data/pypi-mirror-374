from pydantic import BaseModel

from .column import ColumnSchema


class ModelConfig(BaseModel):
    model_name: str
    class_name: str
    is_duplicate: bool = False
    columns: list[ColumnSchema] = []
