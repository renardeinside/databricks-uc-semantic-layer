from dataclasses import dataclass
from typing import List
from pydantic import BaseModel

class NaturalLanguageQuery(BaseModel):
    payload: str


class SqlQuery(BaseModel):
    query: str


@dataclass
class TableInfo:
    catalog: str
    schema: str
    table: str


@dataclass
class TableInfoWithMetadata(TableInfo):
    columns: List[str]