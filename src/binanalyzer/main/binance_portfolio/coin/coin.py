import logging
from pydantic import BaseModel, field_validator, ValidationError, validate_call
from stats import Stats
from wallet import Wallet
from transactions import Transactions

logger = logging.getLogger("Coin")
logging.basicConfig(level=logging.INFO)


class Coin(BaseModel):
    symbol: str
    stats_obj: Stats | None = None
    wallet_obj: Wallet | None = None
    transactions_obj: Transactions | None = None

    def __init__(self, **data):
        super().__init__(**data)
        self.stats_obj = Stats(symbol=self.symbol)
        # self.wallet_obj = Wallet(symbol=self.symbol)
        # self.transactions_obj = Transactions(symbol=self.symbol)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value):
        if value not in ["BTC", "ETH"]:
            raise ValueError("Symbol error!")
        return value

    class Config:
        validate_assignment = True

    def refresh_stats(self):
        self.stats_obj.refresh()



    # self.wallet_obj = Wallet(symbol)
    # self.transactions_obj = Transactions(symbol)

    #     self.valuation_in_usdt_simple = (
    #         self.stats_obj.buy_price_normal * self.wallet_obj.total_available_coins
    #     )
    #     self.valuation_in_usdt_breakeven = self.valuation_in_usdt_simple / (1 - 0.015)

    #     self.bought_line_simple = 0
    #     self.bought_line_breakeven = 0

    #     if self.wallet_obj.total_available_coins:
    #         self.bought_line_simple = abs(
    #             self.transactions_obj.total_invested_usdt_normal / self.wallet_obj.total_available_coins
    #         )
    #         self.bought_line_breakeven = self.bought_line_simple / (1 - 0.015)

    #     self.transactions = self.transactions_obj.get_filtered_transactions_df(
    #         filter_dict={"coin": self.symbol.lower().strip(), "order_status": "success"}
    #     )

    #     self.lifetime_pnl_normal =  round(self.valuation_in_usdt_breakeven - self.transactions_obj.total_invested_usdt_normal, 4)
    #     self.expected_lifetime_pnl_normal =  round(self.valuation_in_usdt_breakeven - self.transactions_obj.total_invested_usdt_expected, 4)

    # def refresh_stats(self):
    #     self.stats_obj.refresh_stats()
    #     self.valuation_in_usdt_simple = (
    #         self.stats_obj.buy_price_normal * self.wallet_obj.total_available_coins
    #     )
    #     self.valuation_in_usdt_breakeven = self.valuation_in_usdt_simple / (1 - 0.015)

    # def refresh_transactions(self):
    #     self.transactions_obj.refresh_transactions()
    #     if self.wallet_obj.total_available_coins:
    #         self.bought_line_simple = abs(
    #             self.transactions_obj.total_invested_usdt_normal / self.wallet_obj.total_available_coins
    #         )
    #         self.bought_line_breakeven = self.bought_line_simple / (1 - 0.015)
