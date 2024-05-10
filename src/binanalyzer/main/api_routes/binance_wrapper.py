from binanalyzer.main.binance_wrapper.binance_wrapper import BinanceWrapper

from typing import Optional, List, Any
import logging
from pydantic import BaseModel, Field, field_validator, create_model
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import Annotated

logging.basicConfig(level=logging.INFO)

binance_api_wrapper_obj = BinanceAPIWrapper()

router = APIRouter()


# Coin Pair Price -----------------------------------------------------------------------------------------------
class CoinPriceResponse(BaseModel):
    isSuccess: bool
    coinpair_price: dict[str, float]


class CoinPriceRequest(BaseModel):
    coin_name: Optional[str] = Field(
        default=None, title="coin_name", description="Coin Name", max_length=8
    )
    coin_list: Optional[List[str]] = Field(
        default=None, description="List of Coin Names"
    )

    @field_validator("coin_name")
    def validate_coin_name(cls, value):
        if value is None:
            return value
        if value.lower().strip() == "usdt":
            raise ValueError("Coin name cannot be only USDT")
        if "usdt" not in value.lower():
            return value.strip().upper() + "USDT"
        return value.upper()

    @field_validator("coin_list")
    def validate_coin_list(cls, value):
        if value is not None:
            return [cls.validate_coin_name(coin_name) for coin_name in value]
        return value


@router.get(
    "/coinpair_price",
    response_model=CoinPriceResponse,
    summary="Get the current price of the coinpair or coinpairs.",
    description="Get the current price of the coinpair or coinpairs. \
        Provide either a single coin name or a list of coin names.",
)
async def get_coinpair_price(
    coin_name: str = Query(None, title="Coin Name"),
    coin_list: List[str] = Query(None, title="List of Coin Names"),
):
    try:
        request = CoinPriceRequest(coin_name=coin_name, coin_list=coin_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if request.coin_name:
            price = binance_api_wrapper_obj.get_coinpair_price(request.coin_name)
            return CoinPriceResponse(
                isSuccess=True, coinpair_price={request.coin_name: price}
            )
        elif request.coin_list:
            prices_dict = {
                coin_name: binance_api_wrapper_obj.get_coinpair_price(coin_name)
                for coin_name in request.coin_list
            }
            return CoinPriceResponse(isSuccess=True, coinpair_price=prices_dict)
        else:
            raise ValueError("Either coin_name or coin_list must be provided.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# No of coins in Spot Wallet -----------------------------------------------------------------------------------------------
class SpotCoinsResponse(BaseModel):
    isSuccess: bool
    free_coins: float = 0.0
    locked_coins: float = 0.0
    freeze_coins: float = 0.0
    withdrawing_coins: float = 0.0
    ipoable_coins: float = 0.0


class SpotCoinsRequest(BaseModel):
    coin_name: Optional[str] = Field(
        None,
        title="coin_name",
        description="Coin Name",
        max_length=5,
    )

    @field_validator("coin_name")
    def validate_coin_name(cls, value):
        if value is None:
            return value
        return value.upper()


@router.get(
    "/coins_in_spot_wallet",
    response_model=SpotCoinsResponse,
    summary="Get the total no of coins in Binance Spot Wallet.",
)
async def get_coins_in_spot_wallet(
    coin_name: str = Query(None, title="Coin Name"),
):
    try:
        request = SpotCoinsRequest(coin_name=coin_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        response_dict = binance_api_wrapper_obj.get_no_of_coin_from_spot_wallet(
            request.coin_name
        )
        if not response_dict:
            return SpotCoinsResponse(isSuccess=True)

        return SpotCoinsResponse(
            isSuccess=True,
            free_coins=response_dict["free_coins"],
            locked_coins=response_dict["locked_coins"],
            freeze_coins=response_dict["freeze_coins"],
            withdrawing_coins=response_dict["withdrawing_coins"],
            ipoable_coins=response_dict["ipoable_coins"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# No of coins in Funding Wallet -----------------------------------------------------------------------------------------------
class FundingCoinsResponse(BaseModel):
    isSuccess: bool
    free_coins: float = 0.0
    locked_coins: float = 0.0
    freeze_coins: float = 0.0
    withdrawing_coins: float = 0.0


class FundingCoinsRequest(BaseModel):
    coin_name: Optional[str] = Field(
        None,
        title="coin_name",
        description="Coin Name",
        max_length=5,
    )

    @field_validator("coin_name")
    def validate_coin_name(cls, value):
        if value is None:
            return value
        return value.upper()


@router.get(
    "/coins_in_funding_wallet",
    response_model=FundingCoinsResponse,
    summary="Get the total no of coins in Binance Funding Wallet.",
)
async def get_coins_in_funding_wallet(
    coin_name: str = Query(None, title="Coin Name"),
):
    try:
        request = FundingCoinsRequest(coin_name=coin_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        response_dict = binance_api_wrapper_obj.get_no_of_coin_from_funding_wallet(
            request.coin_name
        )
        if not response_dict:
            return FundingCoinsResponse(isSuccess=True)
        return FundingCoinsResponse(
            isSuccess=True,
            free_coins=response_dict["free_coins"],
            locked_coins=response_dict["locked_coins"],
            freeze_coins=response_dict["freeze_coins"],
            withdrawing_coins=response_dict["withdrawing_coins"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# No of coins in Earn Wallet -----------------------------------------------------------------------------------------------
class EarnCoinsResponse(BaseModel):
    isSuccess: bool
    total_coins: float = 0.0


class EarnCoinsRequest(BaseModel):
    coin_name: Optional[str] = Field(
        None,
        title="coin_name",
        description="Coin Name",
        max_length=5,
    )

    @field_validator("coin_name")
    def validate_coin_name(cls, value):
        if value is None:
            return value
        return value.upper()


@router.get(
    "/coins_in_earn_wallet",
    response_model=EarnCoinsResponse,
    summary="Get the total no of coins in Binance Earn Wallet.",
)
async def get_coins_in_earn_wallet(
    coin_name: str = Query(None, title="Coin Name"),
):
    try:
        request = EarnCoinsRequest(coin_name=coin_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        total_coins = binance_api_wrapper_obj.get_no_of_coin_from_earn_wallet(
            request.coin_name
        )
        if not total_coins:
            return EarnCoinsResponse(isSuccess=True)
        return EarnCoinsResponse(
            isSuccess=True,
            total_coins=total_coins,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Convert History -----------------------------------------------------------------------------------------------
class ConvertHistoryResponse(BaseModel):
    isSuccess: bool
    convert_history: List[dict[str, Any]]


@router.get(
    "/get_convert_history",
    response_model=ConvertHistoryResponse,
    summary="Get the total no of coins in Binance Earn Wallet.",
)
async def get_get_convert_history():
    try:
        convert_history = binance_api_wrapper_obj.get_convert_history()
        if not convert_history:
            return ConvertHistoryResponse(isSuccess=True, convert_history=[])
        return ConvertHistoryResponse(
            isSuccess=True,
            convert_history=convert_history["list"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Sync Database -----------------------------------------------------------------------------------------------
class SyncDatabaseResponse(BaseModel):
    isSuccess: bool
    message: str


@router.get(
    "/sync_database",
    response_model=SyncDatabaseResponse,
    summary="Sync the database with the latest transactions from Binance",
)
async def sync_database():
    try:
        binance_api_wrapper_obj.sync_database()
        return SyncDatabaseResponse(isSuccess=True, message="Database Synced Successfully.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
