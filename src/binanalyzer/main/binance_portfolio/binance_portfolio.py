
class BinancePortfolio:
    def __init__(self):
        self.current_coin_obj = None
        self.coin_obj_dict = {}
        self.coin_option_list = self.get_coin_options()
