from robinhood.Robinhood import Robinhood, Intervals, Spans, Bounds
from utils.Config import Config

config = Config(configure_file='../config.json')

rb = Robinhood()
if not rb.login(username=config.get_config('robinhood.username'), password=config.get_config('robinhood.password')):
    print('Login failed.')
    exit()

print("get_crypto_quotes")
currency_pairs = rb.get_crypto_currency_pairs()
currency_pair_by_id = {
      currency_pair['id']: currency_pair for currency_pair in currency_pairs
}

data_set = {}

for symbol in [currency_pair['symbol'].replace('-', '') for currency_pair in currency_pairs]:
    history = rb.get_crypto_historicals(symbol, Intervals.FIVE_MINUTE, Spans.WEEK, Bounds.TWENTYFOUR_SEVEN)
    data_points = history.get('data_points')

    for data_point in data_points:
        if data_point.get('begins_at') not in data_set:
            data_set[data_point['begins_at']] = {}

        data_set[data_point['begins_at']][symbol] = data_point.get('close_price')

for data in data_set:
    prices = [data]
    for symbol in [currency_pair['symbol'].replace('-', '') for currency_pair in currency_pairs]:
        prices.append(data_set.get(data).get(symbol, ''))

    print(','.join(prices))
