from fastapi import FastAPI
import uvicorn
from main.api_routes.db_wrapper import router as db_router
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Starting the FastAPI server")

app = FastAPI()

app.include_router(db_router, prefix="/binanalyzer_database")


if __name__ == "__main__":
    uvicorn.run(
        "binanalyzer_database_service:app", host="0.0.0.0", port=80, reload=True
    )
