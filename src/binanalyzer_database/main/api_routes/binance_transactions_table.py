from flask import Blueprint, jsonify, make_response
from flask import request
from typing import Optional, List, Any
import logging
from pydantic import BaseModel, Field, field_validator

from main.app.binance_transactions_table.binance_transactions_table import (
    BinanceTransactionsTable,
)

logging.basicConfig(level=logging.INFO)

binance_transactions_router = Blueprint(
    "binance_transactions_router", __name__, url_prefix="/binance_transactions"
)

TABLE_OBJ = BinanceTransactionsTable()


# Hello World -----------------------------------------------------------------------------------------------
@binance_transactions_router.route("/hello")
def hello():
    return {"message": "Hello from /binance_transactions/hello"}


# Database Sync -----------------------------------------------------------------------------------------------
class DBSyncRequest(BaseModel):
    transaction_list: Optional[List[dict[str, Any]]] = Field(
        ..., description="List of transactions to sync"
    )

    @field_validator("transaction_list")
    @classmethod
    def validate_transaction_list(cls, value):
        if not value:
            return []
        return value


class DBSyncResponse(BaseModel):
    isSuccess: bool
    description: str


@binance_transactions_router.route("/sync_binance_transactions", methods=["POST"])
def sync_binance_transactions():
    try:
        # Parse JSON data from request
        json_data = request.get_json()
        # Validate data against Pydantic model
        request_obj = DBSyncRequest(**json_data)
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, description=str(e)).model_dump(mode="json"),
            500,
        )
    try:
        TABLE_OBJ.sync_table_with_remote(request_obj.transaction_list)
        return make_response(
            DBSyncResponse(
                isSuccess=True, description="Database synced successfully"
            ).model_dump(mode="json"),
            200,
        )
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, description=str(e)).model_dump(mode="json"),
            500,
        )


# Get row count -----------------------------------------------------------------------------------------------
@binance_transactions_router.route("/row_count", methods=["GET"])
def row_count():
    try:
        row_count = TABLE_OBJ.row_count()
        return make_response(jsonify(row_count), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# Select All -----------------------------------------------------------------------------------------------
class SelectAllResponse(BaseModel):
    isSuccess: bool
    transactions: Optional[List[dict[str, Any]]] = []
    error: Optional[str] = ""


@binance_transactions_router.route("/select_all", methods=["GET"])
def select_all():
    try:
        transaction_list = TABLE_OBJ.select_all()
        return make_response(
            SelectAllResponse(isSuccess=True, transactions=transaction_list).model_dump(
                mode="json"
            ),
            200,
        )
    except Exception as e:
        return make_response(
            SelectAllResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )


# Filter Transaction -----------------------------------------------------------------------------------------------
class FilterTransactionsRequest(BaseModel):
    filter_dict: Optional[dict[str, Any]] = Field(
        ..., description="List of Filters to apply on transactions"
    )

    @field_validator("filter_dict")
    @classmethod
    def validate_filter_dict(cls, value):
        if not value:
            return {}
        return value


class FilterTransactionsResponse(BaseModel):
    isSuccess: bool
    transactions: Optional[List[dict[str, Any]]] = []
    error: Optional[str] = ""


@binance_transactions_router.route("/filter_transactions", methods=["POST"])
def filter_transactions():
    try:
        # Parse JSON data from request
        json_data = request.get_json()
        if not json_data:
            return make_response(
                FilterTransactionsResponse(
                    isSuccess=False, error="No filter_dict sent"
                ).model_dump(mode="json"),
                500,
            )
        # Validate data against Pydantic model
        request_obj = FilterTransactionsRequest(**json_data)
    except Exception as e:
        return make_response(
            FilterTransactionsResponse(isSuccess=False, error=str(e)).model_dump(
                mode="json"
            ),
            500,
        )

    try:
        transaction_list = TABLE_OBJ.filter_transactions(request_obj.filter_dict)
        return make_response(
            FilterTransactionsResponse(
                isSuccess=True, transactions=transaction_list
            ).model_dump(mode="json"),
            200,
        )
    except Exception as e:
        return make_response(
            FilterTransactionsResponse(isSuccess=False, error=str(e)).model_dump(
                mode="json"
            ),
            500,
        )
