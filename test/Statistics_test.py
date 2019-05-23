import calculator.Statistics as statistics
from utils.ml_tool import FifoQueue
import csv
import pandas as pd

queue_3 = FifoQueue(30 * 3)
queue_5 = FifoQueue(30 * 5)

bid_prices = []
last_trade_prices = []
bid_trade_diff_rates = []
history_price_slopes = []

with open('/Users/james.zhou/Git/ml_1/data_set/ZM_output_2019-05-22.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        quote ={
            'bid_price': float(row[3]),
            'last_trade_price': float(row[5])
        }

        queue_3.push(quote)
        queue_5.push(quote)

        bid_trade_diff_rate, history_price_slope = statistics.get_trend(quote, queue_3.get_items())
        # statistics.get_trend(quote, queue_5)

        bid_prices.append(float(row[3]))
        last_trade_prices.append(float(row[5]))
        bid_trade_diff_rates.append(bid_trade_diff_rate)
        history_price_slopes.append(history_price_slope)

        print(queue_3.get_size(), queue_5.get_size(),  quote)

tf = pd.DataFrame(list(zip(bid_prices, last_trade_prices, bid_trade_diff_rates, history_price_slopes))
                  , columns=['bid_prices', 'last_trade_prices', 'bid_trade_diff_rates', 'history_price_slopes'])

print()
