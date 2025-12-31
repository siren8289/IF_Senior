import os
from fastapi import FastAPI
import yaml

app = FastAPI(
    title="IF(이프) API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

swagger_path = os.path.join(
    BASE_DIR,
    "openApi",
    "v1",
    "swagger.yaml"
)

with open(swagger_path, "r", encoding="utf-8") as f:
    openapi_schema = yaml.safe_load(f)

app.openapi_schema = openapi_schema


@app.get("/")
def root():
    return {"status": "ok"}
