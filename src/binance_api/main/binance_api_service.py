from fastapi import FastAPI
import uvicorn
from main.api_routes.binance_wrapper import router as binance_router


app = FastAPI()

app.include_router(binance_router)


@app.get("/hello")
async def get_coinpair_price():
    return "Hello from Binance API!"


if __name__ == "__main__":
    uvicorn.run("binance_api_service:app", host="0.0.0.0", port=8000, reload=True)
