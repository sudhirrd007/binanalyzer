from fastapi import FastAPI
import uvicorn
from main.api_routes.binance_api import router as binance_router
from main.api_routes.database_sync import router as database_router


app = FastAPI()
app.include_router(binance_router)
app.include_router(database_router)


@app.get("/")
async def hello_world():
    return "Hello from Binanalyzer index endpoint!"


@app.get("/hello")
async def hello():
    return "Hello from Binanalyzer home page!"


if __name__ == "__main__":
    uvicorn.run("binanalyzer_service:app", host="0.0.0.0", port=9000, reload=True)
