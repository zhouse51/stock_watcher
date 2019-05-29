from robinhood.Robinhood import Robinhood
from utils.Config import Config
import pandas as pd

config = Config(configure_file='../config.json')
rbh = Robinhood()


def fetch_all_symbols():
    if not rbh.login(username=config.get_config('robinhood.username'),
                     password=config.get_config('robinhood.password')):
        print('Login failed.')
        exit()

    data = rbh.instruments('')
    symbols = []
    symbols += [instrument.get('symbol') for instrument in data.get('results')]

    while data.get('next'):
        data = rbh.get_url(data.get('next'))
        symbols += [instrument.get('symbol') for instrument in data.get('results')]
        print("get next page of list ", len(symbols))

    with open('/Users/james.zhou/Documents/raw_quotes/symbols.csv', 'a') as the_file:
        the_file.write('\n'.join(symbols))


def fetch_historicals(interval='day', span='year'):
    if not rbh.login(username=config.get_config('robinhood.username'),
                     password=config.get_config('robinhood.password')):
        print('Login failed.')
        exit()

    c = 0
    with open('/Users/james.zhou/Documents/raw_quotes/symbols.csv', 'r') as symbol_file:
        for symbol in symbol_file:
            symbol = symbol.strip('\n')
            c += 1
            print('Working on ', '[' + symbol + ']', c)

            stock = rbh.get_historical_quotes(symbol, interval, span)
            if not stock:
                print('No data yet.')
                continue

            historicals = stock.get('historicals')
            with open('/Users/james.zhou/Documents/raw_quotes/historicals_' + interval + '-' + span + '_' + symbol + '.csv', 'a') as the_file:
                for historical in historicals:
                    row = [
                        symbol,
                        historical.get('begins_at'),
                        historical.get('open_price'),
                        historical.get('close_price'),
                        historical.get('high_price'),
                        historical.get('low_price'),
                        str(historical.get('volume'))
                    ]

                    the_file.write(','.join(row) + '\n')
                the_file.flush()

    # print(stock.get('historicals'))


def build_analyze_data():
    c = 0
    with open('/Users/james.zhou/Documents/raw_quotes/symbols.csv', 'r') as symbol_file:
        for symbol in symbol_file:
            symbol = symbol.strip('\n')
            c += 1
            print('Working on ', '[' + symbol + ']', c)
            try:
                df = pd.read_csv('/Users/james.zhou/Documents/raw_quotes/historicals_' + symbol + '.csv')
                df.columns = ['symbol', 'begins_at', 'open_price', 'close_price', 'high_price', 'low_price', 'volume']
                df.set_index('begins_at')
            except:
                continue

            if df['close_price'].iloc[0] == 0:
                continue

            df['a'] = df['open_price'].shift(-3)
            df['b'] = df['close_price'].shift(-3)
            df['c'] = df['high_price'].shift(-3)
            df['d'] = df['low_price'].shift(-3)

            df.dropna()

            df['max'] = df[['open_price', 'close_price', 'high_price', 'low_price', 'a', 'b', 'c', 'd']].max(axis=1)
            df['min'] = df[['open_price', 'close_price', 'high_price', 'low_price', 'a', 'b', 'c', 'd']].min(axis=1)

            df['diff'] = (df['max'] - df['min'])/df['max']

            mean = df['diff'].mean()
            median = df['diff'].median()
            max_positive = df['diff'].max()
            max_negative = df['diff'].min()

            week_diff = df['close_price'].iloc[-1] - df['close_price'].iloc[-5]
            week_diff_rate = (df['close_price'].iloc[-1] - df['close_price'].iloc[-5]) / df['close_price'].iloc[-5]

            month_diff = df['close_price'].iloc[-1] - df['close_price'].iloc[-30]
            month_diff_rate = (df['close_price'].iloc[-1] - df['close_price'].iloc[-30]) / df['close_price'].iloc[-30]

            total_diff = df['close_price'].iloc[-1] - df['close_price'].iloc[0]
            total_diff_rate = (df['close_price'].iloc[-1] - df['close_price'].iloc[0])/df['close_price'].iloc[0]

            latest_close = df['close_price'].iloc[-1]

            with open('/Users/james.zhou/Documents/raw_quotes/statistic.csv', 'a') as the_file:
                row = [
                    symbol,
                    str(mean),
                    str(median),
                    str(max_positive),
                    str(max_negative),

                    str(week_diff),
                    str(week_diff_rate),

                    str(month_diff),
                    str(month_diff_rate),

                    str(total_diff),
                    str(total_diff_rate),

                    str(latest_close)
                ]
                the_file.write(','.join(row) + '\n')
                the_file.flush()


def analyze():
    df = pd.read_csv('/Users/james.zhou/Documents/raw_quotes/statistic.csv')
    df.columns = ['symbol', 'mean', 'median', 'max_positive', 'max_negative', 'week_diff', 'week_diff_rate', 'month_diff', 'month_diff_rate', 'total_diff', 'total_diff_rate', 'latest_close']
    df.set_index('symbol')
    # positive_diff_df = df[df['total_diff_rate'] > 0.5]
    positive_diff_df = df[df['total_diff_rate'] > 0.5][df['month_diff_rate'] > 0.12][df['week_diff_rate'] > 0.03]
    big_amp_df = positive_diff_df[positive_diff_df['median'] > 0.05]
    price_range_df = big_amp_df[big_amp_df['latest_close'] > 10][big_amp_df['latest_close'] <= 100]
    # lt_10_df = gt_10_df[gt_10_df['latest_close'] <= 50]
    print(price_range_df)


# fetch_all_symbols()
# fetch_historicals()
# fetch_historicals(interval='5minute', span='week')
# build_analyze_data()
analyze()
