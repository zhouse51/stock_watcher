from utils.ml_tool import FifoQueue
from scipy.stats import linregress
import utils.ml_tool as util
import datetime


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
        samples_queue[stock] = FifoQueue(number_of_samples)

    return samples_queue


def build_checkpoints(investments):
    checkpoint_rates = [round(1 + r/100, 2) for r in list(range(-20, 21))]
    for stock in investments:
        transaction = investments.get(stock)
        if transaction:
            trans_price = transaction.get('price')
            investments.get(stock)['checkpoint_prices'] = [round(trans_price * checkpoint_rate, 2) for checkpoint_rate in checkpoint_rates]
    return checkpoint_rates


def calculate_slop(stock_period_samples, interval=5, period=10, ask_price_key='ask_price', bid_price_key='bid_price', market_price_key='last_trade_price'):
    number_of_samples = int((60 / interval) * period)

    ask_price_slope = 0
    bid_price_slope = 0
    last_trade_price_slope = 0

    x_value = list(range(0, len(stock_period_samples.get_items()[-1 * number_of_samples:])))

    if len(x_value) > 1:
        ask_price_slope = (linregress(x_value, [float(q.get(ask_price_key)) for q in stock_period_samples.get_items()[-number_of_samples:]])).slope
        bid_price_slope = (linregress(x_value, [float(q.get(bid_price_key)) for q in stock_period_samples.get_items()[-number_of_samples:]])).slope
        last_trade_price_slope = (linregress(x_value, [float(q.get(market_price_key)) for q in stock_period_samples.get_items()[-number_of_samples:]])).slope
    return ask_price_slope, bid_price_slope, last_trade_price_slope


def stocks_details_output(stocks, stock_quotes, fundamentals, interval, checkpoint_rates, period_samples):
    for quote in stock_quotes:
        updated_at = util.uct_to_ny_time(quote.get('updated_at'))
        symbol = quote.get('symbol')
        ask_price = round(float(quote.get('ask_price')), 3)
        ask_size = int(quote.get('ask_size'))
        bid_price = round(float(quote.get('bid_price')), 3)
        bid_size = int(quote.get('bid_size'))
        last_trade_price = round(float(quote.get('last_trade_price')), 3)
        base_line = round(float(quote.get('previous_close')), 3)
        # base_line = round(float(fundamentals.get(symbol).get('open')), 3)

        # calculated data
        today_open_diff = round(((last_trade_price - base_line)/last_trade_price) * 100, 3)
        today_open_diff_output = util.get_diff_output(today_open_diff, format='{:>6}', postfix='%')

        period_samples.get(symbol).push(quote)

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

        bid_trade_diff_rate, history_price_slope, trend_factor, trend = get_trend(quote, period_samples.get(symbol))

        print(f'{symbol:{5}} {updated_at:{8}} '
              f'{ask_price:{9}} ({ask_price_slope_output_5min:{1}}{ask_price_slope_output_10min:{1}}) {ask_size:{4}} '
              f'{bid_price:{9}} ({bid_price_slope_output_5min:{1}}{bid_price_slope_output_10min:{1}}) {bid_size:{4}} '
              f'{last_trade_price:{9}} ({last_trade_price_slope_output_5min:{1}}{last_trade_price_slope_output_10min:{1}}) '
              + '[' + today_open_diff_output + '] '
              + bid_trade_diff_output + ' [' + bid_trade_diff_rate_output + '] ' +
              f' --> {display if display else ""} '
              f'{round(history_price_slope, 3)}, {round(trend_factor,2)}, {trend}'
              )


def store_stock_data(stock_quotes):
    for stock_quote in stock_quotes:
        # raw data
        updated_at = util.uct_to_ny_time(stock_quote.get('updated_at'))
        symbol = stock_quote.get('symbol')
        ask_price = stock_quote.get('ask_price')
        ask_size = stock_quote.get('ask_size')
        bid_price = stock_quote.get('bid_price')
        bid_size = stock_quote.get('bid_size')
        last_trade_price = stock_quote.get('last_trade_price')

        with open('../data_set/' + symbol + '_output_' + datetime.today().strftime("%Y-%m-%d") + '.csv', 'a') as the_file:
            line = str(updated_at) + ',' + str(ask_price) + ',' + str(ask_size) + ',' + str(bid_price) + ',' + str(bid_size) + ',' + str(last_trade_price)
            the_file.write(line + '\n')
            the_file.flush()
            the_file.close()


def BTC_details_output(btc_transaction, btc_quote, interval, checkpoint_rates, period_samples):
    updated_at = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
    ask_price = round(float(btc_quote.get('ask_price')), 3)
    bid_price = round(float(btc_quote.get('bid_price')), 3)
    mark_price = round(float(btc_quote.get('mark_price')), 3)
    volumn = btc_quote.get('volume')

    previous_quote = period_samples.get('BTCUSD').peek_last()
    previous_volumn = previous_quote.get('volume', 0) if previous_quote else 0

    volumn = round(float(volumn) - float(previous_volumn), 2)

    # calculated data
    period_samples.get('BTCUSD').push(btc_quote)

    ask_price_slope_3min, bid_price_slope_3min, market_price_slope_3min = calculate_slop(period_samples.get('BTCUSD'), interval=interval, period=3, market_price_key='mark_price')
    ask_price_slope_10min, bid_price_slope_10min, mark_price_slope_10min = calculate_slop(period_samples.get('BTCUSD'), interval=interval, period=10, market_price_key='mark_price')

    ask_price_slope_output_3min = util.get_slop_output(ask_price_slope_3min)
    bid_price_slope_output_3min = util.get_slop_output(bid_price_slope_3min)
    mark_price_slope_output_3min = util.get_slop_output(market_price_slope_3min)

    ask_price_slope_output_10min = util.get_slop_output(ask_price_slope_10min)
    bid_price_slope_output_10min = util.get_slop_output(bid_price_slope_10min)
    mark_price_slope_output_10min = util.get_slop_output(mark_price_slope_10min)

    bid_trade_diff = round(mark_price - bid_price, 3)
    bid_trade_diff_rate = round(((mark_price - bid_price) / mark_price) * 100, 2)
    bid_trade_diff_output = util.get_diff_output(bid_trade_diff)
    bid_trade_diff_rate_output = util.get_diff_output(bid_trade_diff_rate, format='{:>5}', postfix='%')

    trans_price = btc_transaction.get('price')
    trans_type = btc_transaction.get('type')
    trans_unit_price = btc_transaction.get('unit_price')
    shares = btc_transaction.get('shares', 0)

    if btc_transaction.get('type') == 'buy':
        total_value = bid_price * shares
        trans_price_diff = round(total_value - trans_price, 2) if trans_type == 'buy' else 0
        trans_price_diff_rate = round((trans_price_diff / trans_price) * 100, 2)
    else:
        total_value = ask_price * shares
        trans_price_diff = round(total_value - trans_price, 2) if trans_type == 'buy' else 0
        trans_price_diff_rate = round((trans_price_diff / trans_price) * 100, 2)

    total_value_output = util.get_diff_output(round(total_value, 2), format='{:>6}', postfix='$')
    total_price_diff_output = util.get_diff_output(trans_price_diff, format='{:>6}', postfix='$')
    trans_price_diff_rate_output = util.get_diff_output(trans_price_diff_rate, format='{:>5}', postfix='%')

    display = '[' + trans_price_diff_rate_output + '] '
    display += '[' + total_price_diff_output + '] [' + total_value_output + ']' if trans_type == 'buy' else ''

    bid_trade_diff_rate, history_price_slope, trend_factor, trend = get_trend(btc_quote, period_samples.get('BTCUSD'), multiplier=[50, 1], factor=[0.0, 1], market_price_key='mark_price')

    print(f'{updated_at:{5}} '
          f'{volumn:{9}} '
          f'{ask_price:{9}} ({ask_price_slope_output_3min:{1}}{ask_price_slope_output_10min:{1}}) '
          f'{bid_price:{9}} ({bid_price_slope_output_3min:{1}}{bid_price_slope_output_10min:{1}}) '
          f'{mark_price:{9}} ({mark_price_slope_output_3min:{1}}{mark_price_slope_output_10min:{1}}) '
          + bid_trade_diff_output + ' [' + bid_trade_diff_rate_output + '] ' +
          f' --> {display if display else ""} '
          f'{round(history_price_slope, 3)}, {round(trend_factor, 2)}, {trend}'
          )


def store_btc_data(btc_quote):
    # raw data
    updated_at = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    ask_price = btc_quote.get('ask_price')
    bid_price = btc_quote.get('bid_price')
    mark_price = btc_quote.get('mark_price')
    high_price = btc_quote.get('high_price')
    low_price = btc_quote.get('low_price')
    open_price = btc_quote.get('open_price')
    volume = btc_quote.get('volume')
    row = [updated_at, ask_price, bid_price, mark_price, high_price, low_price, open_price, volume]

    with open('/Users/james.zhou/Documents/raw_quotes/btc_output_' + datetime.datetime.today().strftime("%Y-%m-%d") + '.csv', 'a') as the_file:
        the_file.write(','.join(row) + '\n')
        the_file.flush()
        the_file.close()


def get_trend(quote, history_quote_queue, interval=5, period=3, multiplier=[50, 71], factor=[0.4, 0.6], ask_price_key='ask_price', bid_price_key='bid_price', market_price_key='last_trade_price'):
    number_of_samples = int((60 / interval) * period)

    # bid_trade_diff_rate range -0.02 ~ +0.02 (-3% ~ +3%)
    quote_bid_price = float(quote.get(bid_price_key))
    quote_last_trade_price = float(quote.get(market_price_key))
    bid_trade_diff_rate = ((quote_last_trade_price - quote_bid_price) / quote_last_trade_price)

    # slop range -0.004 ~ 0.004
    x_value = list(range(0, len(history_quote_queue.get_items()[-1 * number_of_samples:])))
    y_value = [float(history_quote.get(market_price_key)) for history_quote in history_quote_queue.get_items()[-number_of_samples:]]
    history_price_slope = 0
    if len(x_value) > 1:
        history_price_slope = (linregress(x_value, y_value)).slope

    # TODO factor need to be in params from config
    trend_factor = (bid_trade_diff_rate * multiplier[0]) * factor[0] + (history_price_slope * multiplier[1]) * factor[1]
    # +: up, -: down
    # range 0 ~ +/-1, can be over
    # 0 ~ 0.2: slow: 1
    # 0.2 ~ 0.5: mild: 2
    # >= 0.5: fast: 3
    # > 1.0: over: 4
    # TREND: -2, -1, 0, 1, 2
    trend = 0 if abs(trend_factor) == 0 else (1 if abs(trend_factor) < 0.2 else (2 if abs(trend_factor) < 0.5 else (3 if abs(trend_factor) < 1 else 4)))
    trend = (-1 * trend) if trend_factor < 0 else trend

    # print('diff: ' + str(bid_trade_diff_rate) + ', slop: ' + str(history_price_slope) + ', factor: ' + str(trend_factor) + ', trend: ' + str(trend))

    return bid_trade_diff_rate, history_price_slope, trend_factor, trend
