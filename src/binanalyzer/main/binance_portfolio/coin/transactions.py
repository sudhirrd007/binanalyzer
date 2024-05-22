# from sqlite_wrapper.sqlite_wrapper import SQLiteWrapper
# import logging
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)


# class Transactions:
#     def __init__(self, symbol):
#         self.sqlite_wrapper = SQLiteWrapper()
#         self.symbol = symbol
#         self.transactions_history_df = {}

#         self.total_buy_normal = 0
#         self.total_sell_normal = 0
#         self.total_invested_usdt_normal = 0
#         self.total_buy_expected = 0
#         self.total_sell_expected = 0
#         self.total_invested_usdt_expected = 0
#         self.refresh_transactions()

#     def refresh_transactions(self):
#         self.total_buy_normal = 0
#         self.total_sell_normal = 0
#         self.total_invested_usdt_normal = 0
#         self.total_invested_usdt_expected = 0

#         self.transactions_history_df = self.get_filtered_transactions_df(
#             filter_dict={"coin": self.symbol.lower().strip(), "order_status": "success"}
#         )
#         logging.info(
#             "Total records filtered for %s: %s",
#             self.symbol,
#             self.transactions_history_df.shape[0],
#         )
#         previous_timestamp = None
#         for row in self.transactions_history_df.iterrows():
#             row = row[1]
#             buy_amount = 0
#             sell_amount = 0
#             current_timestamp = row["timestamp"]
#             if row["order_status"].lower().strip() == "success":
#                 if row["buy_sell"]:
#                     buy_amount = row["usdt_equivalent"]
#                     self.total_buy_normal += buy_amount
#                 else:
#                     sell_amount = row["usdt_equivalent"]
#                     self.total_sell_normal += sell_amount

#                 # Normal ---------------------
#                 self.total_invested_usdt_normal += buy_amount - sell_amount

#                 # with returns ---------------------
#                 if previous_timestamp is None:
#                     self.total_invested_usdt_expected += buy_amount - sell_amount
#                 else:
#                     returns_amount = returns_till_date(
#                         notional=self.total_invested_usdt_expected,
#                         days=days_between_timestamps(
#                             previous_timestamp, current_timestamp
#                         ),
#                     )
#                     self.total_invested_usdt_expected += returns_amount + (
#                         buy_amount - sell_amount
#                     )

#                 previous_timestamp = current_timestamp

#                 # # with returns sell
#                 # if previous_timestamp is None:
#                 #     self.total_buy_expected = buy_amount
#                 # else:
#                 #     self.total_buy_expected += buy_amount + returns_till_date(
#                 #         notional=buy_amount,
#                 #         days=days_between_timestamps(
#                 #             previous_timestamp, row["timestamp"]
#                 #         ),
#                 #     )


#     def get_filtered_transactions_df(self, filter_dict=None):
#         return self.sqlite_wrapper.database_manager_obj.filter_transactions_df(
#             filter_dict=filter_dict
#         )


# def days_between_timestamps(timestamp1, timestamp2):
#     # Calculate the difference in days
#     delta = timestamp2 - timestamp1

#     seconds_per_day = 24 * 60 * 60
#     milliseconds_per_day = seconds_per_day * 1000

#     # Convert milliseconds to days
#     days = abs(delta) / milliseconds_per_day
#     # Return the absolute number of full days
#     return days


# def returns_till_date(notional, days, returns_perc_rate=5):
#     # Calculate the returns
#     returns_amount = ((returns_perc_rate / 365.25) / 100) * notional * days
#     return returns_amount
