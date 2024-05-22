# import logging
# from binance_wrapper.binanace_wrapper import BinanceWrapper
# from sqlite_wrapper.sqlite_wrapper import SQLiteWrapper

# logging.basicConfig(level=logging.INFO)


# class Wallet:
#     def __init__(self, symbol):
#         self.binance_wrapper = BinanceWrapper()
#         self.symbol = symbol
#         self.coin_holdings_dict = 0
#         self.total_available_coins = 0
#         self.refresh_wallet()

#     def refresh_wallet(self):
#         self.coin_holdings_dict = self.get_total_no_of_coins(self.symbol)
#         self.total_available_coins = self.coin_holdings_dict["total_coins"]

#     def get_total_no_of_coins(self, symbol):
#         symbol = symbol.upper().strip()
#         return self.binance_wrapper.get_total_no_of_coins(symbol)
