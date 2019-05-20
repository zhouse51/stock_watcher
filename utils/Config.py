import json


class Config(object):
    config = {}

    def __init__(self, configure_file='config.json'):
        with open(configure_file, 'r') as fp:
            data = json.load(fp)
            self.config['robinhood.username'] = data['credential']['robinhood']['username']
            self.config['robinhood.password'] = data['credential']['robinhood']['password']
            self.config['aws.access_key_id'] = data['credential']['aws']['aws_access_key_id']
            self.config['aws.secret_access_key'] = data['credential']['aws']['aws_secret_access_key']
            self.config['aws.region'] = data['credential']['aws']['region']
            self.config['fetch_interval'] = data['fetch_interval']
            fp.close()

    def get_config(self, key):
        return self.config.get(key, None)
