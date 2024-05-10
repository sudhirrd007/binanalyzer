from typing import Optional, List, Any
import logging
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, Query, Body

from main.db_wrapper.db_wrapper import DBWrapper

logging.basicConfig(level=logging.INFO)

db_wrapper_obj = DBWrapper()

router = APIRouter()

# Hello World -----------------------------------------------------------------------------------------------
@router.get("/hello", summary="Hello World", description="Hello World")
async def hello():
    return {"message": "Hello World"}


# Database Sync -----------------------------------------------------------------------------------------------
class DBSyncRequest(BaseModel):
    transaction_list: Optional[List[dict[str, Any]]] = Field(
        ..., description="List of transactions to sync"
    )

    @field_validator("transaction_list")
    def validate_transaction_list(cls, value):
        if len(value) == 0:
            print(">>> Empty List")
            return []
        required_columns = set(
            [
                "order_id",
                "quote_id",
                "coin",
                "timezone",
                "timestamp",
                "year",
                "month",
                "day",
                "time",
                "order_status",
                "automatically_added",
                "coin_amount",
                "conversion_ratio",
                "usdt_equivalent",
                "trade_type",
                "buy_sell",
                "miscellaneous",
            ]
        )
        for row in value:
            request_columns = set(row.keys())
            diff = required_columns - request_columns
            if diff:
                raise ValueError(f"Columns missing in the transaction list: {diff}")
        return value


class DBSyncResponse(BaseModel):
    isSuccess: bool
    message: Optional[str] = ""
    error: Optional[str] = ""


@router.post(
    "/sync_database",
    response_model=DBSyncResponse,
    summary="Sync the database with the provided transactions",
    description="Sync the database with the provided transactions",
)
async def sync_database(transaction_list: List[dict[str, Any]] = Body()):
    # print(">>>>", transaction_list)
    try:
        request = DBSyncRequest(transaction_list=transaction_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # print(">>>>>>>>>>>>", transaction_list)
    try:
        db_wrapper_obj.db_sync(request.transaction_list)
        return DBSyncResponse(isSuccess=True, message="Database synced successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
