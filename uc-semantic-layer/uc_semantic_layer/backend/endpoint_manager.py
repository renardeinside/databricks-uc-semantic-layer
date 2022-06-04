import os 
from uc_semantic_layer.backend.models import TableInfo, TableInfoWithMetadata
from dataclasses import asdict
from databricks import sql
from typing import List


class EndpointManager:
    def __init__(self, logger) -> None:
        self._logger = logger
        self._conn = self._get_connection()
        self._catalog = os.getenv("DBSQL_CATALOG")
        self._schema = os.getenv("DBSQL_SCHEMA")
        self.table_infos = self.get_table_infos_with_metadata()

    def _get_connection(self):
        self._logger.info("Initializing DBSQL connection")
        connection = sql.connect(
            server_hostname=os.getenv("DBSQL_SERVER_HOSTNAME"),
            http_path=os.getenv("DBSQL_HTTP_PATH"),
            access_token=os.getenv("DBSQL_ACCESS_TOKEN"),
        )
        self._logger.info("Initializing DBSQL connection - done!")
        return connection
    
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
            self._logger.info(f"Collecting information for table {table}")
            columns = self.get_columns_per_table(table)
            _collected.append(TableInfoWithMetadata(**asdict(table), columns=columns))
        return _collected

    def execute_query(self, query: str, limit: int = 100):
        with self._conn.cursor() as c:
            return c.execute(query).fetchmany_arrow(limit)

