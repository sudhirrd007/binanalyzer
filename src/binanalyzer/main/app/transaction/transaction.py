from pydantic import field_validator
import logging
from sqlmodel import Field, SQLModel
from pydantic import field_validator


class Transaction(SQLModel, table=True):
    __tablename__ = "binance_transactions"

    order_id: str = Field(
        default=None,
        primary_key=True,
    )
    quote_id: str = None
    coin: str = None
    coin_amount: float = Field(
        description=f"ALTER TABLE {__tablename__} MODIFY COLUMN coin_amount DOUBLE;",
        default=None,
    )
    usdt_equivalent: float = Field(
        description=f"ALTER TABLE {__tablename__} MODIFY COLUMN usdt_equivalent DOUBLE;",
        default=None,
    )
    buy_sell: bool = None
    timestamp: int = Field(
        description=f"ALTER TABLE {__tablename__} MODIFY COLUMN timestamp BIGINT;",
        default=None,
    )
    timezone: str = None
    year: int = None
    month: int = None
    day: int = None
    time: str = None
    order_status: str = None
    trade_type: str = None
    automatically_added: bool = None
    conversion_ratio: float = Field(
        description=f"ALTER TABLE {__tablename__} MODIFY COLUMN conversion_ratio DOUBLE;",
        default=None,
    )
    miscellaneous: str = Field(
        description=f"ALTER TABLE {__tablename__} MODIFY COLUMN miscellaneous TEXT;",
        default=None,
    )

    class Config:
        validate_assignment = True

    @field_validator("coin")
    @classmethod
    def validate_coin(cls, value):
        if not value:
            return None
        return value.upper()
