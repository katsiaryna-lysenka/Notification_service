from typing import Optional

from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

app = FastAPI()


app.mongodb_client: Optional[MongoClient] = None  # type: ignore


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
async def shutdown_db_client():
    if app.mongodb_client is not None:
        app.mongodb_client.close()
