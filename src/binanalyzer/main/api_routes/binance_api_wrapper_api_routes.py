from main.binance_api_wrapper.binance_api_wrapper import BinanceAPIWrapper

import logging
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

logging.basicConfig(level=logging.INFO)

router = APIRouter()

class CoinPriceResponse(BaseModel):
    isSuccess: bool
    coinpair_price: float

# Dependency to create a new instance of the wrapper class for each request
def get_binance_api_wrapper():
    return BinanceAPIWrapper()

@router.post("/coinpair_price", response_model=CoinPriceResponse)
def coinpair_price(coin_name: str, wrapper: BinanceAPIWrapper = Depends(get_binance_api_wrapper)):
    """Get the current price of the coinpair"""
    try:
        logging.info(f"coin_name: {coin_name}")
        price = wrapper.get_coinpair_price(f"{coin_name.upper()}USDT")
        logging.info(f"coinpair_price: {price}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"isSuccess": True, "coinpair_price": price}
