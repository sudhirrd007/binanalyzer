from fastapi import FastAPI
import uvicorn
from main.api_routes.binance_api import router as binance_router


app = FastAPI()

app.include_router(binance_router)


@app.get("/")
async def hello_world():
    return "Hello from Binanalyzer index endpoint!"


@app.get("/hello")
async def hello():
    return "Hello from Binanalyzer home page!"


if __name__ == "__main__":
    uvicorn.run("TEMP_binanalyzer_service:app", host="0.0.0.0", port=8000, reload=True)
