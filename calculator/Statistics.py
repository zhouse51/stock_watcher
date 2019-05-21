from utils.ml_tool import FifoQueue, Color
from scipy.stats import linregress
import utils.ml_tool as util


def init_period_sample_sequence(stocks, interval=5, period=10):
    '''
    :param stocks:
    :param interval: refresh interval in seconds
    :param period: in minutes
    :return:
    '''

    period_samples = []
    number_of_samples = (60 / interval) * period
    samples_queue = {}
    for stock in stocks:
        samples_queue[stock] = {
            'ask_price': FifoQueue(number_of_samples),
            'bid_price': FifoQueue(number_of_samples),
            'last_trade_price': FifoQueue(number_of_samples),
        }
    # period_samples.append(samples)

    return samples_queue


def build_checkpoints(stocks):
    checkpoint_rates = [round(1 + r/100, 2) for r in list(range(-20, 21))]
    for stock in stocks:
        transaction = stocks.get(stock)
        if transaction:
            trans_price = transaction.get('price')
            stocks.get(stock)['checkpoint_prices'] = [round(trans_price * checkpoint_rate, 2) for checkpoint_rate in checkpoint_rates]
    return checkpoint_rates


def calculate_slop(stock_period_samples, interval=5, period=10):
    number_of_samples = int((60 / interval) * period)

    ask_price_slope = 0
    bid_price_slope = 0
    last_trade_price_slope = 0

    x_value = list(range(0, len(stock_period_samples.get('ask_price').get_items()[-1 * number_of_samples:])))
    if len(x_value) > 1:
        ask_price_slope = (linregress(x_value, stock_period_samples.get('ask_price').get_items()[-number_of_samples:])).slope
        bid_price_slope = (linregress(x_value, stock_period_samples.get('bid_price').get_items()[-number_of_samples:])).slope
        last_trade_price_slope = (linregress(x_value, stock_period_samples.get('last_trade_price').get_items()[-number_of_samples:])).slope
    return ask_price_slope, bid_price_slope, last_trade_price_slope


def details_output(stocks, stock_quotes, fundamentals, interval, checkpoint_rates, period_samples):
    for stock_quote in stock_quotes:
        updated_at = util.uct_to_ny_time(stock_quote.get('updated_at'))
        symbol = stock_quote.get('symbol')
        ask_price = round(float(stock_quote.get('ask_price')), 3)
        ask_size = int(stock_quote.get('ask_size'))
        bid_price = round(float(stock_quote.get('bid_price')), 3)
        bid_size = int(stock_quote.get('bid_size'))
        last_trade_price = round(float(stock_quote.get('last_trade_price')), 3)
        base_line = round(float(stock_quote.get('previous_close')), 3)
        # base_line = round(float(fundamentals.get(symbol).get('open')), 3)

        # calculated data
        today_open_diff = round(((last_trade_price - base_line)/last_trade_price) * 100, 3)
        today_open_diff_output = util.get_diff_output(today_open_diff, format='{:>6}', postfix='%')

        period_samples.get(symbol).get('ask_price').push(ask_price)
        period_samples.get(symbol).get('bid_price').push(bid_price)
        period_samples.get(symbol).get('last_trade_price').push(last_trade_price)

        ask_price_slope_5min, bid_price_slope_5min, last_trade_price_slope_5min = calculate_slop(period_samples.get(symbol), interval=interval, period=5)
        ask_price_slope_10min, bid_price_slope_10min, last_trade_price_slope_10min = calculate_slop(period_samples.get(symbol), interval=interval, period=10)

        ask_price_slope_output_5min = util.get_slop_output(ask_price_slope_5min)
        bid_price_slope_output_5min = util.get_slop_output(bid_price_slope_5min)
        last_trade_price_slope_output_5min = util.get_slop_output(last_trade_price_slope_5min)

        ask_price_slope_output_10min = util.get_slop_output(ask_price_slope_10min)
        bid_price_slope_output_10min = util.get_slop_output(bid_price_slope_10min)
        last_trade_price_slope_output_10min = util.get_slop_output(last_trade_price_slope_10min)

        bid_trade_diff = round(last_trade_price - bid_price, 3)
        bid_trade_diff_rate = round(((last_trade_price - bid_price) / last_trade_price) * 100, 2)
        bid_trade_diff_output = util.get_diff_output(bid_trade_diff)
        bid_trade_diff_rate_output = util.get_diff_output(bid_trade_diff_rate, format='{:>5}', postfix='%')

        transaction = stocks.get(symbol, None)
        display = None
        if transaction:
            trans_price = transaction.get('price')
            trans_type = transaction.get('type')
            shares = transaction.get('shares', 0)

            trans_price_per_share_diff = round((last_trade_price - trans_price), 2)
            total_price_diff = round(trans_price_per_share_diff * shares, 2) if trans_type == 'buy' else 0
            trans_price_diff_rate = round((trans_price_per_share_diff / trans_price) * 100, 2)

            trans_price_per_share_diff_output = util.get_diff_output(trans_price_per_share_diff, format='{:>6}', postfix='$')
            total_price_diff_output = util.get_diff_output(total_price_diff, format='{:>6}', postfix='$')
            trans_price_diff_rate_output = util.get_diff_output(trans_price_diff_rate, format='{:>5}', postfix='%')

            display = '[SELL] [' + trans_price_per_share_diff_output + '] [' + trans_price_diff_rate_output + '] '
            display += '[' + total_price_diff_output + ']' if trans_type == 'buy' else ''

            checkpoint_prices = transaction.get('checkpoint_prices')
            for i in range(0, len(checkpoint_rates)):
                if last_trade_price < checkpoint_prices[i]:
                    position = checkpoint_prices[i - 2:i] + ['*'] + checkpoint_prices[i:i + 2]

                    lower_bound = util.get_diff_output(i - 22, format='{:>2}', postfix='%')
                    higher_bound = util.get_diff_output(i - 19, format='{:2}', postfix='%')
                    display += f' {lower_bound:{3}} >[ {" > ".join([util.get_level_output(p, trans_price) for p in position])} ]> {higher_bound:{3}}'
                    break

        print(f'{symbol:{5}} {updated_at:{8}} '
              f'{ask_price:{9}} ({ask_price_slope_output_5min:{1}}{ask_price_slope_output_10min:{1}}) {ask_size:{4}} '
              f'{bid_price:{9}} ({bid_price_slope_output_5min:{1}}{bid_price_slope_output_10min:{1}}) {bid_size:{4}} '
              f'{last_trade_price:{9}} ({last_trade_price_slope_output_5min:{1}}{last_trade_price_slope_output_10min:{1}}) '
              + '[' + today_open_diff_output + '] '
              + bid_trade_diff_output + ' [' + bid_trade_diff_rate_output + '] ' +
              f' --> {display if display else ""}'
              )