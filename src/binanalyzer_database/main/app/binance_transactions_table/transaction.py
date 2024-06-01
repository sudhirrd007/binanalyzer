from pydantic import BaseModel


class Transaction(BaseModel):
    order_id: str
    quote_id: str
    coin: str
    timezone: str
    timestamp: int
    year: int
    month: int
    day: int
    time: str
    order_status: str
    automatically_added: bool
    coin_amount: float
    conversion_ratio: float
    usdt_equivalent: float
    trade_type: str
    buy_sell: bool
    miscellaneous: str

    def create_insert_query(self):
        keys = self.model_fields.keys()
        insert_query = (
            "INSERT INTO binance_transactions (" + ", ".join(keys) + ") VALUES ("
        )
        for key in keys:
            if self.model_fields[key].annotation == str:
                insert_query += f"'{getattr(self, key)}'"
            else:
                insert_query += f"{getattr(self, key)}"
            insert_query += ", "
        insert_query = insert_query[:-2] + ");"
        return insert_query
