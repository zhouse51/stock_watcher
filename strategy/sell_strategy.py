from datetime import datetime
from utils.ml_tool import FifoQueue
from calculator.Statistics import get_trend


class SellStrategy(object):
    stop_loss_rate_adjusted = False

    def __init__(self, buy_transaction, refresh_rate=5, base_profitable_rate=0.03, stop_loss_rate=0.03):
        self.buy_transaction = buy_transaction
        self.refresh_rate = refresh_rate
        self.today_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.quote_queue = FifoQueue()

        self.base_profitable_rate = 1 + base_profitable_rate
        self.base_profitable_price = self.buy_transaction.get('price') * (1 + base_profitable_rate)
        self.adjusted_profitable_rate = self.base_profitable_rate
        self.adjusted_profitable_price = self.base_profitable_price
        self.adjusted_down_profitable_rate = self.adjusted_profitable_rate * 0.99
        self.adjusted_down_profitable_price = self.adjusted_profitable_price * 0.99

        self.stop_loss_rate = stop_loss_rate
        self.stop_loss_price = self.buy_transaction.get('price') * (1 - stop_loss_rate)

        self.stop_loss_rate_adjusted = False
        self.base_profitable_price_reached = False
        self.adjusted_profitable_rate_reached = False

        self.trend_history = FifoQueue(3 * 60 / refresh_rate)

    def suggest(self, quote, history_quote_queue):
        decision_trace = []

        decision = False
        # do not trade in the same day
        if self.buy_transaction.get('date') == self.today_date:
            decision_trace.append('0')
            decision = False
        else:
            decision_trace.append('1')

            trade_price = float(quote.get('last_trade_price'))

            bid_trade_diff_rate, history_price_slope, trend_factor, trend = get_trend(quote, history_quote_queue, interval=self.refresh_rate, period=5, multiplier=[50, 71], factor=[0.3, 0.7])
            self.trend_history.push(trend)

            if trade_price <= self.stop_loss_price:
                decision_trace.append('2-1')

                if trend < -2:
                    decision_trace.append('3-1')
                    if self.stop_loss_rate_adjusted:
                        decision_trace.append('4-1')
                        decision = True
                    else:
                        decision_trace.append('4-2')
                        self.stop_loss_rate = self.stop_loss_rate * 1.01
                        self.stop_loss_price = self.buy_transaction.get('price') * (1 - self.stop_loss_rate)
                        decision = False
                else:
                    decision_trace.append('3-2')
                    decision = True

                self.stop_loss_rate_adjusted = True
            else:
                decision_trace.append('2-2')
                if trade_price > self.base_profitable_price:
                    decision_trace.append('3-4')
                    if self.base_profitable_price_reached:
                        decision_trace.append('4-6')
                        if trade_price > self.adjusted_profitable_price:
                            decision_trace.append('5-3')
                            self.adjusted_down_profitable_rate = self.adjusted_profitable_rate * 0.99
                            self.adjusted_down_profitable_price = self.adjusted_profitable_price * 0.99
                            self.adjusted_profitable_rate = self.adjusted_profitable_rate * 1.01
                            self.adjusted_profitable_price = self.adjusted_profitable_price * 1.01

                            decision = False
                        else:
                            decision_trace.append('5-4')
                            if trade_price < self.adjusted_down_profitable_price:
                                decision_trace.append('6-3')

                                if trend < -2:
                                    decision_trace.append('7-2')
                                    decision = True
                                else:
                                    decision_trace.append('7-1')
                                    trend_avg = sum(self.trend_history.get_items()) / self.trend_history.get_size()
                                    if trend_avg < -1:
                                        decision_trace.append('8-2')
                                        decision = True
                                    else:
                                        decision_trace.append('8-1')
                                        decision = False

                            else:
                                decision_trace.append('6-4')
                                decision = False
                    else:
                        decision_trace.append('4-5')
                        self.base_profitable_price_reached = True
                        self.adjusted_down_profitable_rate = self.adjusted_profitable_rate * 0.99
                        self.adjusted_down_profitable_price = self.adjusted_profitable_price * 0.99
                        self.adjusted_profitable_rate = self.adjusted_profitable_rate * 1.01
                        self.adjusted_profitable_price = self.adjusted_profitable_price * 1.01

                        decision = False

                else:
                    decision_trace.append('3-3')
                    if self.base_profitable_price_reached:
                        decision_trace.append('4-4')
                        if trade_price > self.base_profitable_price * 0.99:
                            decision_trace.append('5-1')

                            if trend < -2:
                                decision_trace.append('6-1')
                                decision = True
                            else:
                                decision_trace.append('6-2')
                                decision = False

                        else:
                            decision_trace.append('5-2')
                            decision = True
                    else:
                        decision_trace.append('4-3')
                        decision = False

        # print(decision_trace, decision)
        return ' > '.join(decision_trace), decision
