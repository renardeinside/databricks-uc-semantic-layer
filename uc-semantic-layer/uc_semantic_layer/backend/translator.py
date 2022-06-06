
from typing import List
from uc_semantic_layer.backend.models import TableInfoWithMetadata
import openai
import os 

class Translator:
    def __init__(self, logger, table_infos_with_metadata: List[TableInfoWithMetadata]) -> None:
        self._logger = logger
        self._tables = table_infos_with_metadata
        openai.api_key = os.getenv("OPENAI_API_KEY")

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
        self._logger.info("Prepared prompt:")
        self._logger.info(_expression)
        return "\n".join([el.strip() for el in _expression.split("\n")])
    
    def _process_api_response(self, prepared_prompt: str, max_tokens: int = 1200):
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
    
    def get_sql_query(self, query: str) -> str:
        prepared_prompt = self.prepare(query)
        generated_sql_query = self._process_api_response(prepared_prompt)
        return generated_sql_query
