import calculator.Statistics as statistics
from utils.ml_tool import FifoQueue
import csv
import pandas as pd
import matplotlib.pyplot as plt

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
        # bid_trade_diff_rate, history_price_slope = statistics.get_trend(quote, queue_5.get_items())

        bid_prices.append(float(row[3]))
        last_trade_prices.append(float(row[5]))
        bid_trade_diff_rates.append(bid_trade_diff_rate)
        history_price_slopes.append(history_price_slope)

        # print(queue_3.get_size(), queue_5.get_size(),  quote)

tf = pd.DataFrame(list(zip(bid_prices, last_trade_prices, bid_trade_diff_rates, history_price_slopes))
                  , columns=['bid_prices', 'last_trade_prices', 'bid_trade_diff_rates', 'history_price_slopes'])

print()
print(tf['bid_trade_diff_rates'].max())
print(tf['bid_trade_diff_rates'].median())
print(tf['bid_trade_diff_rates'].min())
print()
print(tf['history_price_slopes'][8:].max())
print(tf['history_price_slopes'][8:].median())
print(tf['history_price_slopes'][8:].min())

t = list(tf.index)
fig, ax1 = plt.subplots(figsize=(15, 10))
# ax1.plot(t, stock_data['ask_price'], color='r')
ax1.plot(t, tf['bid_prices'], color='r')
# ax1.plot(t, stock_data['bid_price'], color='b')
ax1.plot(t, tf['bid_prices'], color='b')
# ax1.plot(t, stock_data['last_trade_price'], color='g')
ax1.plot(t, tf['last_trade_prices'], color='g')

# ax2 = ax1.twinx()
# ax2.bar(t, tf['ask_size'], align='center', alpha=0.5, color='m')
# ax2.plot(t, tf['mean_ask_size_' + str(period)], color='m')
# ax2.bar(t, tf['bid_size'], align='center', alpha=0.5, color='c')
# ax2.plot(t, tf['mean_bid_size_' + str(period)], color='c')
plt.show()

print()
