from datetime import datetime
from utils.ml_tool import FifoQueue
from calculator.Statistics import get_trend


class BuyStrategy(object):
    def __init__(self, sell_transaction, refresh_rate=5, base_profitable_rate=0.03, stop_loss_rate=0.03):
        self.sell_transaction = sell_transaction
        self.refresh_rate = refresh_rate
        self.today_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.quote_queue = FifoQueue()

    def suggest(self, quote, history_quote_queue):
        decision_trace = []

        decision = False

        return ' > '.join(decision_trace), decision