from flask import Blueprint, jsonify, make_response
from flask import request
from typing import Optional, List, Any
import logging
from pydantic import BaseModel, Field, field_validator

from main.db_wrapper.db_wrapper import DBWrapper

logging.basicConfig(level=logging.INFO)

db_wrapper_obj = DBWrapper()

db_blueprint = Blueprint("db_blueprint", __name__, url_prefix="/binanalyzer_database")


# Hello World -----------------------------------------------------------------------------------------------
@db_blueprint.route("/hello")
def hello():
    return {"message": "Hello from the Database!"}


# # Database Sync -----------------------------------------------------------------------------------------------
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


@db_blueprint.route("/sync_database", methods=["POST"])
def sync_database():
    try:
        # Parse JSON data from request
        json_data = request.get_json()
        # Validate data against Pydantic model
        request_obj = DBSyncRequest(**json_data)
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )
    try:
        db_wrapper_obj.db_sync(request_obj.transaction_list)
        return make_response(
            DBSyncResponse(
                isSuccess=True, message="Database synced successfully"
            ).model_dump(mode="json"),
            200,
        )
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )


# Fetch All Transactions -----------------------------------------------------------------------------------------------
class FetchAllTransactionsResponse(BaseModel):
    isSuccess: bool
    transactions: Optional[List[dict[str, Any]]] = []
    error: Optional[str] = ""


@db_blueprint.route("/fetch_all_transactions", methods=["GET"])
def fetch_all_transactions():
    try:
        transaction_list = db_wrapper_obj.fetch_all_transactions()
        return make_response(
            FetchAllTransactionsResponse(
                isSuccess=True, transactions=transaction_list
            ).model_dump(mode="json"),
            200,
        )
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )


# Filter Transaction -----------------------------------------------------------------------------------------------
class FilterTransactionsRequest(BaseModel):
    filter_dict: Optional[dict[str, Any]] = Field(
        ..., description="List of Filters to apply on transactions"
    )

    @field_validator("filter_dict")
    def validate_filter_dict(cls, value):
        if not value:
            return {}
        available_columns = set(
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
        request_columns = set(value.keys())
        diff = request_columns - available_columns
        if diff:
            raise ValueError(f"Unexpected filter found: {diff}")
        return value


class FilterTransactionsResponse(BaseModel):
    isSuccess: bool
    transactions: Optional[List[dict[str, Any]]] = []
    error: Optional[str] = ""


@db_blueprint.route("/fetch_filtered_transactions", methods=["POST"])
def fetch_filtered_transactions():
    try:
        # Parse JSON data from request
        json_data = request.get_json()
        # Validate data against Pydantic model
        request_obj = FilterTransactionsRequest(**json_data)
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )

    try:
        transaction_list = db_wrapper_obj.filter_transactions(request_obj.filter_dict)
        return make_response(
            FilterTransactionsResponse(
                isSuccess=True, transactions=transaction_list
            ).model_dump(mode="json"),
            200,
        )
    except Exception as e:
        return make_response(
            DBSyncResponse(isSuccess=False, error=str(e)).model_dump(mode="json"),
            500,
        )
