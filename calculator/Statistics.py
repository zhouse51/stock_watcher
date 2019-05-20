from utils.ml_tool import FifoQueue, Color
from scipy.stats import linregress


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
