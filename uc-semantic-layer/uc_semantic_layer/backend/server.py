import re
from typing import List
from databricks.sql.exc import ServerOperationError
import os
from fastapi import FastAPI, HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware

from dataclasses import dataclass, asdict
from uc_semantic_layer.backend.models import NaturalLanguageQuery, SqlQuery, TableInfo, TableInfoWithMetadata
from uc_semantic_layer.backend.endpoint_manager import EndpointManager
from uc_semantic_layer.backend.translator import Translator

logger = logging.getLogger("uc_semantic_layer")

CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
]


app = FastAPI()

endpoint_manager = EndpointManager(logger)
translator = Translator(logger, endpoint_manager.table_infos)


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


@app.post("/sql_query")
def sql_query(req: NaturalLanguageQuery):
    return {"query": translator.get_sql_query(req.payload)}


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
