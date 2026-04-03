import logging
from datetime import datetime
import pytz
import json
from pydantic import BaseModel
from typing import Any, Union

logging.basicConfig(level=logging.INFO)


class BinanceTransaction(BaseModel):
    quoteId: Union[str, int, float]  # done
    orderId: Union[str, int, float]  # done
    orderStatus: Any
    fromAsset: str
    fromAmount: Union[str, int, float]
    toAsset: str
    toAmount: Union[str, int, float]
    ratio: Any
    inverseRatio: Any
    createTime: Union[str, int, float]  # done
    orderType: str
    side: Any

    def convert_to_transaction(self):
        transaction = {}
        transaction["quote_id"] = validate_empty_string("quoteId", self.quoteId)
        transaction["order_id"] = validate_empty_string("orderId", self.orderId)

        (
            transaction["coin"],
            transaction["coin_amount"],
            transaction["usdt_equivalent"],
            transaction["buy_sell"],
        ) = validate_coin_coinamount_usdtequivalent_buysell(
            fromAsset=self.fromAsset,
            fromAmount=self.fromAmount,
            toAsset=self.toAsset,
            toAmount=self.toAmount,
        )

        transaction["timestamp"] = validate_timestamp(timestamp=self.createTime)
        transaction["timezone"] = "US/Eastern"
        (
            transaction["year"],
            transaction["month"],
            transaction["day"],
            transaction["time"],
        ) = validate_year_month_day_time(
            timestamp=transaction["timestamp"], timezone=transaction["timezone"]
        )

        transaction["order_status"] = validate_order_status(
            order_status=self.orderStatus
        )  # success, failed, open, pending, in progress

        transaction["trade_type"] = validate_trade_type(
            trade_type=self.orderType
        )  # market, limit, stop, stop limit, oco, conversion

        if transaction["buy_sell"]:
            transaction["conversion_ratio"] = float(self.inverseRatio)
        else:
            transaction["conversion_ratio"] = float(self.ratio)

        transaction["miscellaneous"] = validate_miscellaneous(miscellaneous=None)
        return transaction


# Validations ------------------------------------------------------
def validate_year_month_day_time(timestamp, timezone):
    datetime_obj = datetime.fromtimestamp(
        timestamp / 1000,
        tz=pytz.timezone(timezone),
    )
    year = datetime_obj.year
    if year < 100:
        year += 2000  # current century: 2000
    month = datetime_obj.month
    day = datetime_obj.day
    time_str = datetime_obj.time().strftime("%H:%M:%S")
    try:
        datetime(year=year, month=month, day=day)
    except Exception as e:
        logging.error(f"Date is not valid: {e}")
        raise ValueError(f"Date is not valid: {e}")
    return year, month, day, time_str


def validate_timestamp(timestamp):
    """
    Normalize any given timestamp to a datetime object, assuming the timestamp
    is in milliseconds when it has 13 digits.

    If the timestamp is longer or shorter than 13 digits, it will be adjusted
    by either removing excess digits from the left (assuming they represent
    smaller units than milliseconds) or by padding with zeros (assuming the
    missing digits represent milliseconds).

    :param timestamp: The timestamp to normalize, which can be of any digit length.
    :return: A datetime object representing the given timestamp adjusted to milliseconds.
    """
    # Try converting the timestamp to an float if it is a string
    if isinstance(timestamp, str):
        if not timestamp.strip():
            logging.error(f"Timestamp is Empty: {timestamp}")
            raise ValueError(f"Timestamp is Empty: {timestamp}")
        try:
            float(timestamp)
        except Exception:
            logging.error(f"Timestamp is not valid: {timestamp}")
            raise ValueError(f"Timestamp is not valid: {timestamp}")

    # Determine the timestamp magnitude
    timestamp_str = str(timestamp)
    timestamp_str = timestamp_str.strip()
    timestamp_str = timestamp_str.replace(".", "")

    # Ensure the timestamp is 13 digits long
    if len(timestamp_str) > 13:
        # If longer, take the right-most 13 digits (assuming the left-most digits are beyond millisecond precision)
        normalized_timestamp_str = timestamp_str[:13]
    elif len(timestamp_str) < 13:
        # If shorter, pad with zeros on the left (assuming the missing digits are milliseconds)
        normalized_timestamp_str = timestamp_str.ljust(13, "0")
    else:
        normalized_timestamp_str = timestamp_str

    # Convert back to integer, assuming the result is in milliseconds
    normalized_timestamp_ms = int(normalized_timestamp_str)

    return normalized_timestamp_ms


def validate_order_status(order_status):
    valid_order_statuses = [
        "success",
        "failed",
        "open",
        "pending",
        "in progress",
        "process",
        "fail",
    ]
    if order_status.strip().lower() in valid_order_statuses:
        return order_status.strip().lower()
    logging.error(f"order_status is not valid: {order_status}")
    raise ValueError(f"order_status is not valid: {order_status}")


def validate_coin_coinamount_usdtequivalent_buysell(
    fromAsset, fromAmount, toAsset, toAmount
):
    if toAsset.upper() == "USDT":
        coin = fromAsset
        coin_amount = float(fromAmount)
        usdt_equivalent = float(toAmount)
        buy_sell = False
    elif fromAsset.upper() == "USDT":
        coin = toAsset
        coin_amount = float(toAmount)
        usdt_equivalent = float(fromAmount)
        buy_sell = True
    else:
        print("Error: USDT not found in trans_dict")
        raise ValueError("Error: USDT not found")
    return coin, coin_amount, usdt_equivalent, buy_sell


def validate_trade_type(trade_type):
    valid_trade_types = [
        "market",
        "limit",
        "stop",
        "stop limit",
        "oco",
        "conversion",
    ]
    if trade_type.strip().lower() in valid_trade_types:
        return trade_type.strip().lower()
    logging.error(f"trade_type is not valid: {trade_type}")
    raise ValueError(f"trade_type is not valid: {trade_type}")


def validate_miscellaneous(miscellaneous=None):
    if not miscellaneous:
        return ""
    if isinstance(miscellaneous, dict):
        return json.dumps(miscellaneous)
    if isinstance(miscellaneous, str):
        return miscellaneous
    return ""


def validate_empty_string(key, value):
    if not str(value).strip():
        logging.error(f"Value is Empty: {key}")
        raise ValueError(f"Value is Empty: {value}")
    return str(value)
