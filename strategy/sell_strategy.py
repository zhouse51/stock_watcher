from datetime import datetime
from utils.ml_tool import FifoQueue

class SellStrategy(object):
    stop_loss_rate_adjusted = False

    def __inif__(self, buy_transaction, refresh_rate=5, base_profitable_rate=0.04, stop_loss_rate=-0.03):
        self.buy_transaction = buy_transaction
        self.today_date = datetime.strptime(datetime.now(), '%Y-%m-%d')
        self.quote_queue = FifoQueue()
        self.base_profitable_rate = base_profitable_rate
        self.adjusted_profitable_rate = base_profitable_rate
        self.stop_loss_rate = stop_loss_rate

        self.stop_loss_rate_adjusted = False
        self.base_profitable_rate_reached = False
        self.adjusted_profitable_rate_reached = False


    def suggest(self, quote):
        decision = False
        # do not trade in the same day
        if self.buy_transaction.get('date') == self.today_date:
            return False

        quote_ask_price = float(quote.get('ask_price'))
        quote_ask_size = int(quote.get('ask_size'))
        quote_bid_price = float(quote.get('bid_price'))
        quote_bid_size = int(quote.get('bid_size'))
        quote_last_trade_price = float(quote.get('last_trade_price'))
        bid_trade_diff_rate = ((quote_last_trade_price - quote_bid_price) / quote_last_trade_price)

        trans_buy_price = self.buy_transaction.get('price')

        # if reach base_profitable_rate
        if (quote_last_trade_price - trans_buy_price) / trans_buy_price > self.base_profitable_rate:
            self.base_profitable_rate_reached = True

        if (quote_last_trade_price - trans_buy_price)/trans_buy_price > self.adjusted_profitable_rate:
            # if reach profitable_rate
            self.adjusted_profitable_rate_reached = True
            if bid_trade_diff_rate >= 0.004:
                # sharp up, wait
                self.adjusted_profitable_rate = self.adjusted_profitable_rate * 1.01
                decision = False


        elif self.adjusted_profitable_rate_reached:
            # if reached adjusted profitable_rate

                # if sharp down: sell


            decision = True

        elif self.adjusted_profitable_rate_reached:
            # if reached base profitable_rate

            decision = True




        elif (quote_last_trade_price - trans_buy_price)/trans_buy_price < self.stop_loss_rate:
            # if reach stop_loss_rate

            if bid_trade_diff_rate <= -0.004:
                # sharp down
                decision = True
            elif self.stop_loss_rate_adjusted:
                # already adjusted stop loss rate
                decision = True
            else:
                # slow down, adjust the stop loss ratio, decrease 5% more on stop_loss_rate
                self.stop_loss_rate_adjusted = True
                self.stop_loss_rate = self.stop_loss_rate * 1.05
                decision = False


        self.quote_queue.push(quote)
        return decision
