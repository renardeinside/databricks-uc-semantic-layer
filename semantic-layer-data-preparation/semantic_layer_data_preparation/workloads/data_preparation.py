from semantic_layer_data_preparation.common import Workload
from typing import List
from pathlib import Path


class DataPreparationJob(Workload):
    SRC_LOCATION = "dbfs:/databricks-datasets/tpch/delta-001"

    def list_directories(self) -> List[Path]:
        paths = [
            Path(p.path) for p in self.dbutils.fs.ls(self.SRC_LOCATION) if p.isDir()
        ]
        return paths

    def launch(self):

        catalog = self.conf["catalog"]
        database = self.conf["database"]

        self.spark.sql(
            f"CREATE DATABASE IF NOT EXISTS {catalog}.{database}"
        )

        for path in self.list_directories():
            table_name = f"{catalog}.{database}.{path.name}"
            self.logger.info(f"Writing table {table_name}")
            df = self.spark.read.format("delta").load(str(path))
            df.writeTo(table_name).createOrReplace()
            self.logger.info(f"Writing table {table_name} - done")


def entrypoint():  # pragma: no cover
    job = DataPreparationJob()
    job.launch()


# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == "__main__":
    entrypoint()
