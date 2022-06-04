from typing import List
from databricks import sql
from databricks.sql.exc import ServerOperationError
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from fastapi.middleware.cors import CORSMiddleware
import openai
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
]


def get_connection():
    logger.info("Initializing DBSQL connection")
    connection = sql.connect(
        server_hostname=os.getenv("DBSQL_SERVER_HOSTNAME"),
        http_path=os.getenv("DBSQL_HTTP_PATH"),
        access_token=os.getenv("DBSQL_ACCESS_TOKEN"),
    )
    logger.info("Initializing DBSQL connection - done!")
    return connection


class NaturalQuery(BaseModel):
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


class EndpointManager:
    def __init__(self, connection, catalog, schema) -> None:
        self._conn = connection
        self._catalog = catalog
        self._schema = schema

    def get_table_infos(self) -> List[TableInfo]:
        with self._conn.cursor() as c:
            table_names = (
                c.tables(catalog_name=self._catalog, schema_name=self._schema)
                .fetchall_arrow()
                .to_pandas()["TABLE_NAME"]
            )
            table_infos = [
                TableInfo(self._catalog, self._schema, table_name)
                for table_name in table_names
            ]
            return table_infos

    def get_columns_per_table(self, table_info: TableInfo) -> List[str]:
        with self._conn.cursor() as c:
            column_names = (
                c.columns(
                    catalog_name=table_info.catalog,
                    schema_name=table_info.schema,
                    table_name=table_info.table,
                )
                .fetchall_arrow()
                .to_pandas()["COLUMN_NAME"]
            )
            return column_names.to_list()

    def get_table_infos_with_metadata(self) -> List[TableInfoWithMetadata]:
        table_infos = self.get_table_infos()
        _collected = []
        for table in table_infos:
            logger.info(f"Collecting information for table {table}")
            columns = self.get_columns_per_table(table)
            _collected.append(TableInfoWithMetadata(**asdict(table), columns=columns))
        return _collected

    def execute_query(self, query: str):
        with self._conn.cursor() as c:
            return c.execute(query).fetchmany_arrow(100)


class PromptConstructor:
    def __init__(self, table_infos_with_metadata: List[TableInfoWithMetadata]) -> None:
        self._tables = table_infos_with_metadata

    def _get_tables_payload(self) -> str:
        payload = "\n\t# ".join(
            f"{t.catalog}.{t.schema}.{t.table}({','.join(t.columns)})"
            for t in self._tables
        )
        return payload

    def prepare(self, natural_language_query: str) -> str:
        _expression = f"""\
        ### Databricks SQL tables, with their properties:
        #
        # {self._get_tables_payload()}
        #
        ### {natural_language_query}
        SELECT 
        """
        return "\n".join([el.strip() for el in _expression.split("\n")])


app = FastAPI()
connection = get_connection()
endpoint_manager = EndpointManager(
    connection, os.getenv("DBSQL_CATALOG"), os.getenv("DBSQL_SCHEMA")
)
table_infos_with_metadata = endpoint_manager.get_table_infos_with_metadata()

openai.api_key = os.getenv("OPENAI_API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def read_root():
    return {"status": "working"}


def get_sql_query(prepared_prompt: str, max_tokens: int = 300):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prepared_prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["#", ";"],
    )
    return f'SELECT {response["choices"][0].text}'


@app.post("/sql_query")
def sql_query(req: NaturalQuery):
    constructor = PromptConstructor(table_infos_with_metadata)
    prepared_prompt = constructor.prepare(req.payload)
    generated_sql_query = get_sql_query(prepared_prompt)
    return {"query": generated_sql_query}


@app.post("/execute_sql")
def sql_query(req: SqlQuery):
    try:
        result = endpoint_manager.execute_query(req.query).to_pandas()
        # converting results for bootstrap table format
        formatted = {
            "columns": [{"dataField": c, "text": c} for c in result.columns],
            "data": [r.to_dict() for _, r in result.iterrows()],
        }
        return formatted
    except ServerOperationError as e:
        raise HTTPException(status_code=404, detail=e.message)
