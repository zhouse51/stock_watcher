from robinhood.Robinhood import Robinhood
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.Config import Config
import utils.ml_tool as util
import calculator.Statistics as statistics

# TODO load from data store
stocks = {
    # 'NDAQ': None,
    # 'ZM': {
    #     'price': 79.46,
    #     'type': 'sell',
    #     'shares': 7
    # },
    'PINS': {
        'price': 26.48,
        'type': 'buy',
        'shares': 0
    },
    # 'BYND': None,
    'LK': None
    }


def calculate_details(stock_quotes):
    for stock_quote in stock_quotes:
        updated_at = util.uct_to_ny_time(stock_quote.get('updated_at'))
        symbol = stock_quote.get('symbol')
        ask_price = round(float(stock_quote.get('ask_price')), 3)
        ask_size = int(stock_quote.get('ask_size'))
        bid_price = round(float(stock_quote.get('bid_price')), 3)
        bid_size = int(stock_quote.get('bid_size'))
        last_trade_price = round(float(stock_quote.get('last_trade_price')), 3)

        # calculated data
        period_samples.get(symbol).get('ask_price').push(ask_price)
        period_samples.get(symbol).get('bid_price').push(bid_price)
        period_samples.get(symbol).get('last_trade_price').push(last_trade_price)

        ask_price_slope_5min, bid_price_slope_5min, last_trade_price_slope_5min = statistics.calculate_slop(period_samples.get(symbol), interval=interval, period=5)
        ask_price_slope_10min, bid_price_slope_10min, last_trade_price_slope_10min = statistics.calculate_slop(period_samples.get(symbol), interval=interval, period=10)

        ask_price_slope_output_5min = util.get_slop_output(ask_price_slope_5min)
        bid_price_slope_output_5min = util.get_slop_output(bid_price_slope_5min)
        last_trade_price_slope_output_5min = util.get_slop_output(last_trade_price_slope_5min)

        ask_price_slope_output_10min = util.get_slop_output(ask_price_slope_10min)
        bid_price_slope_output_10min = util.get_slop_output(bid_price_slope_10min)
        last_trade_price_slope_output_10min = util.get_slop_output(last_trade_price_slope_10min)

        bid_trade_diff = round(last_trade_price - bid_price, 3)
        bid_trade_diff_rate = round(((last_trade_price - bid_price) / last_trade_price) * 100, 2)
        bid_trade_diff_output = util.get_diff_output(bid_trade_diff)
        bid_trade_diff_rate_output = util.get_diff_output(bid_trade_diff_rate, postfix='%')

        transaction = stocks.get(symbol, None)
        display = None
        if transaction:
            trans_price = transaction.get('price')
            trans_type = transaction.get('type')
            shares = transaction.get('shares', 0)

            trans_price_per_share_diff = round((last_trade_price - trans_price), 2)
            total_price_diff = round(trans_price_per_share_diff * shares, 2) if trans_type == 'buy' else 0
            trans_price_diff_rate = round((trans_price_per_share_diff / trans_price) * 100, 2)

            trans_price_per_share_diff_output = util.get_diff_output(trans_price_per_share_diff)
            total_price_diff_output = util.get_diff_output(total_price_diff)
            trans_price_diff_rate_output = util.get_diff_output(trans_price_diff_rate)

            display = f'[SELL] [{trans_price_per_share_diff_output:{5}}$] [{trans_price_diff_rate_output:{5}}%] '
            display += f'[{total_price_diff_output:{6}}$] ' if trans_type == 'buy' else f'[{"":{7}}] '

            checkpoint_prices = transaction.get('checkpoint_prices')
            for i in range(0, len(checkpoint_rates)):
                if last_trade_price < checkpoint_prices[i]:
                    position = checkpoint_prices[i - 2:i] + ['*'] + checkpoint_prices[i:i + 2]

                    lower_bound = util.get_diff_output(i - 22, postfix='%')
                    higher_bound = util.get_diff_output(i - 19, postfix='%')
                    display += f'{lower_bound:{3}} >[ {" > ".join([util.a(p, trans_price) for p in position])} ]> {higher_bound:{3}}'
                    break

        print(f'{symbol:{6}} {updated_at:{9}} '
              f'{ask_price:{9}} ({ask_price_slope_output_5min:{1}}{ask_price_slope_output_10min:{1}}) '
              f'{bid_price:{9}} ({bid_price_slope_output_5min:{1}}{bid_price_slope_output_10min:{1}}) '
              f'{last_trade_price:{9}} ({last_trade_price_slope_output_5min:{1}}{last_trade_price_slope_output_10min:{1}}) '
              f'{bid_trade_diff_output:{7}} {"[" + bid_trade_diff_rate_output + "]":{7}} '
              f'--> {display if display else ""}'
              )


def process_data():
    stock_quotes = rbh.quotes_data([symbol for symbol in stocks])

    calculate_details(stock_quotes)
    # store_data(stock_quotes)


config = Config()
rbh = Robinhood()

interval = config.get_config('fetch_interval')

checkpoint_rates = statistics.build_checkpoints(stocks)
period_samples = statistics.init_period_sample_sequence(stocks)

if not rbh.login(username=config.get_config('robinhood.username'), password=config.get_config('robinhood.password')):
    print('Login failed.')
    exit()

scheduler = BlockingScheduler()
job = scheduler.add_job(process_data, 'interval', seconds=interval)
scheduler.start()

rbh.logout()