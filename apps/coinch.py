from robinhood.Robinhood import Robinhood
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.Config import Config
import calculator.Statistics as statistics

# TODO load from data store
btc = {
     'BTCUSD': {
        'date': '2019-05-22',
        'price': 90.06,
        'unit_price': 7827.67,
        'type': 'buy',
        'shares': 0.01150479
    }
}


def process_data():
    btc_quote = rbh.get_crypto_quotes(symbols=['BTCUSD']).get('results')
    statistics.BTC_details_output(btc.get('BTCUSD'), btc_quote[0], interval, checkpoint_rates, period_samples)
    # statistics.store_data(stock_quotes)


config = Config(configure_file='../config.json')
rbh = Robinhood()

interval = config.get_config('fetch_interval')

checkpoint_rates = statistics.build_checkpoints(btc)
period_samples = statistics.init_period_sample_sequence(btc)

if not rbh.login(username=config.get_config('robinhood.username'), password=config.get_config('robinhood.password')):
    print('Login failed.')
    exit()

scheduler = BlockingScheduler()
job = scheduler.add_job(process_data, 'interval', seconds=interval)
scheduler.start()

rbh.logout()