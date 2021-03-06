from robinhood.Robinhood import Robinhood
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.Config import Config
import calculator.Statistics as statistics

# TODO load from data store
stocks = {
    # 'NDAQ': None,
    'ZM': {
        'date': '2019-05-22',
        'price': 84.88,
        'type': 'buy',
        'shares': 11
    },
    # 'PINS': {
    #     'price': 26.48,
    #     'type': 'buy',
    #     'shares': 15
    # },
    # 'BYND': None,
    # 'LK': None
    }


def process_data():
    stock_quotes = rbh.quotes_data([symbol for symbol in stocks])
    fundamentals = {
        symbol: rbh.get_fundamentals(symbol) for symbol in stocks
    }

    statistics.stocks_details_output(stocks, stock_quotes, fundamentals, interval, checkpoint_rates, period_samples)
    # statistics.store_data(stock_quotes)


config = Config(configure_file='../config.json')
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
