# crypto from https://github.com/mstrum/robinhood-python

#Standard libraries
import logging
import warnings
from enum import Enum

import requests
from urllib.parse import unquote

#Application-specific imports
from . import exceptions as RH_exception
from . import endpoints


class Intervals(Enum):
    FIFTEEN_SECOND = '15second'
    FIVE_MINUTE = '5minute'
    TEN_MINUTE = '10minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'


class Spans(Enum):
    DAY = 'day'
    HOUR = 'hour'
    WEEK = 'week'
    YEAR = 'year'
    FIVE_YEAR = '5year'
    ALL = 'all'


class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint """

    TWENTYFOUR_SEVEN = '24_7'
    REGULAR = 'regular'
    EXTENDED = 'extended'
    TRADING = 'trading'


class Transaction(Enum):
    """Enum for buy/sell orders """

    BUY = 'buy'
    SELL = 'sell'


class Robinhood:
    """Wrapper class for fetching/parsing Robinhood endpoints """

    session = None
    username = None
    password = None
    headers = None
    auth_token = None
    refresh_token = None

    logger = logging.getLogger('Robinhood')
    logger.addHandler(logging.NullHandler())

    client_id = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"

    def __init__(self):
        self.session = requests.session()
        # self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers
        self.auth_method = self.login_prompt

    def login_required(function):  # pylint: disable=E0213
        """ Decorator function that prompts user for login if they are not logged in already. Can be applied to any function using the @ notation. """

        def wrapper(self, *args, **kwargs):
            if 'Authorization' not in self.headers:
                self.auth_method()
            return function(self, *args, **kwargs)  # pylint: disable=E1102

        return wrapper

    def login_prompt(self):  # pragma: no cover
        """Prompts user for username and password and calls login() """

        username = input("Username: ")
        password = input("Password: ")

        return self.login(username=username, password=password)

    def login(self, username, password, mfa_code=None):
        """Save and test login info for Robinhood accounts
        Args:
            username (str): username
            password (str): password
            mfa_code (str): mfa code, default to None
        Returns:
            (bool): received valid auth token
        """

        self.username = username
        self.password = password
        payload = {
            'password': self.password,
            'username': self.username,
            'grant_type': 'password',
            'client_id': self.client_id,

            'device_token': 'c95c47d2-3118-4c0b-9e40-37b4177365be',
            'expires_in': 86400,
            'scope': 'internal'
        }

        if mfa_code:
            payload['mfa_code'] = mfa_code
        try:
            res = self.session.post(endpoints.login(), data=payload, timeout=15)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.LoginFailed()

        if 'mfa_required' in data.keys():  # pragma: no cover
            raise RH_exception.TwoFactorRequired()  # requires a second call to enable 2FA

        if 'access_token' in data.keys() and 'refresh_token' in data.keys():
            self.auth_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.headers['Authorization'] = 'Bearer ' + self.auth_token
            return True

        return False

    def logout(self):
        """Logout from Robinhood
        Returns:
            (:obj:`requests.request`) result from logout endpoint
        """

        try:
            payload = {
                'client_id': self.client_id,
                'token': self.refresh_token
            }
            req = self.session.post(endpoints.logout(), data=payload, timeout=15)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None

        return req

    ###########################################################################
    #                               GET DATA
    ###########################################################################

    def investment_profile(self):
        """Fetch investment_profile """

        res = self.session.get(endpoints.investment_profile(), timeout=15)
        res.raise_for_status()  # will throw without auth
        data = res.json()

        return data

    def instruments(self, stock):
        """Fetch instruments endpoint
            Args:
                stock (str): stock ticker
            Returns:
                (:obj:`dict`): JSON contents from `instruments` endpoint
        """

        res = self.session.get(endpoints.instruments(), params={'query': stock.upper()}, timeout=15)
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        if stock == "":
            return res

        return res['results']

    def instrument(self, symbol):
        """Fetch instrument info
            Args:
                symbol (str): instrument id
            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(endpoints.instruments()) + "?symbol=" + str(symbol)

        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidInstrumentId()

        return data['results']

    def quote_data(self, stock=''):
        """Fetch stock quote
            Args:
                stock (str): stock ticker, prompt if blank
            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """

        url = None

        if stock.find(',') == -1:
            url = str(endpoints.quotes()) + str(stock) + "/"
        else:
            url = str(endpoints.quotes()) + "?symbols=" + str(stock)

        # Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data

    def quotes_data(self, stocks):
        """Fetch quote for multiple stocks, in one single Robinhood API call
            Args:
                stocks (list<str>): stock tickers
            Returns:
                (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
                    same order of input args. If any ticker is invalid, a None will occur at that position.
        """

        url = str(endpoints.quotes()) + "?symbols=" + ",".join(stocks)

        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data["results"]

    def get_quote_list(self,
                       stock='',
                       key=''):
        """Returns multiple stock info and keys from quote_data (prompt if blank)
            Args:
                stock (str): stock ticker (or tickers separated by a comma)
                , prompt if blank
                key (str): key attributes that the function should return
            Returns:
                (:obj:`list`): Returns values from each stock or empty list
                               if none of the stocks were valid
        """

        # Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            keys = key.split(',')
            myStr = ''
            for item in keys:
                myStr += stock[item] + ","

            return (myStr.split(','))

        # Prompt for stock if not entered
        if not stock:  # pragma: no cover
            stock = input("Symbol: ")

        data = self.quote_data(stock)
        res = []

        # Handles the case of multple tickers
        if stock.find(',') != -1:
            for stock in data['results']:
                if stock is None:
                    continue
                res.append(append_stock(stock))

        else:
            res.append(append_stock(data))

        return res

    def get_historical_quotes(self, stock, interval, span, bounds=Bounds.REGULAR):
        """Fetch historical data for stock
            Note: valid interval/span configs
                interval = 5minute | 10minute + span = day, week
                interval = day + span = year
                interval = week
                TODO: NEEDS TESTS
            Args:
                stock (str): stock ticker
                interval (str): resolution of data
                span (str): length of data
                bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours
            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint
        """
        if type(stock) is str:
            stock = [stock]

        if isinstance(bounds, str):  # recast to Enum
            bounds = Bounds(bounds)

        historicals = endpoints.historicals() + "/?symbols=" + ','.join(stock).upper() + "&interval=" + interval + "&span=" + span + "&bounds=" + bounds.name.lower()

        res = self.session.get(historicals, timeout=15)

        return res.json()['results'][0] if 'results' in res.json() else None

    def get_rating(self, stock):
        url = endpoints.rating() + stock + '/'
        response = self.session.get(url, timeout=15)
        return response.json()

    def get_news(self, stock):
        """Fetch news endpoint
            Args:
                stock (str): stock ticker
            Returns:
                (:obj:`dict`) values returned from `news` endpoint
        """

        return self.session.get(endpoints.news(stock.upper()), timeout=15).json()

    def get_account(self):
        """Fetch account information
            Returns:
                (:obj:`dict`): `accounts` endpoint payload
        """

        res = self.session.get(endpoints.accounts(), timeout=15)
        res.raise_for_status()  # auth required
        res = res.json()

        return res['results'][0]

    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """

        return self.session.get(url, timeout=15).json()

    def get_popularity(self, stock=''):
        """Get the number of robinhood users who own the given stock
            Args:
                stock (str): stock ticker
            Returns:
                (int): number of users who own the stock
        """
        stock_instrument = self.get_url(self.quote_data(stock)["instrument"])["id"]
        return self.get_url(endpoints.instruments(stock_instrument, "popularity"))["num_open_positions"]

    def get_tickers_by_tag(self, tag=None):
        """Get a list of instruments belonging to a tag
            Args: tag - Tags may include but are not limited to:
                * top-movers
                * etf
                * 100-most-popular
                * mutual-fund
                * finance
                * cap-weighted
                * investment-trust-or-fund
            Returns:
                (List): a list of Ticker strings
        """
        instrument_list = self.get_url(endpoints.tags(tag))["instruments"]
        return [self.get_url(instrument)["symbol"] for instrument in instrument_list]

    @login_required
    def get_transfers(self):
        """Returns a page of list of transfers made to/from the Bank.
        Note that this is a paginated response. The consumer will have to look
        at 'next' key in the JSON and make a subsequent request for the next
        page.
            Returns:
                (list): List of all transfers to/from the bank.
        """
        res = self.session.get(endpoints.ach('transfers'), timeout=15)
        res.raise_for_status()
        return res.json()

    ###########################################################################
    #                           GET OPTIONS INFO
    ###########################################################################

    def get_options(self, stock, expiration_dates, option_type):
        """Get a list (chain) of options contracts belonging to a particular stock
            Args: stock ticker (str),
                  list of expiration dates to filter on (YYYY-MM-DD)
                  option type (str) whether or not its a 'put' or a 'call'
            Returns:
                Options Contracts (List): a list (chain) of contracts for a given underlying equity instrument
        """
        instrument_id = self.get_url(self.quote_data(stock)["instrument"])["id"]
        if (type(expiration_dates) == list):
            _expiration_dates_string = ",".join(expiration_dates)
        else:
            _expiration_dates_string = expiration_dates
        chain_id = self.get_url(endpoints.chain(instrument_id))["results"][0]["id"]
        return [contract for contract in self.get_url(endpoints.options(chain_id, _expiration_dates_string, option_type))["results"]]

    @login_required
    def get_option_market_data(self, optionid):
        """Gets a list of market data for a given optionid.
        Args: (str) option id
        Returns: dictionary of options market data.
        """
        market_data = {}
        try:
            market_data = self.get_url(endpoints.market_data(optionid)) or {}
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidOptionId()
        return market_data

    ###########################################################################
    #                           GET FUNDAMENTALS
    ###########################################################################

    def get_fundamentals(self, stock=''):
        """Find stock fundamentals data
            Args:
                (str): stock ticker
            Returns:
                (:obj:`dict`): contents of `fundamentals` endpoint
        """

        # Prompt for stock if not entered
        if not stock:  # pragma: no cover
            stock = input("Symbol: ")

        url = str(endpoints.fundamentals(str(stock.upper())))

        # Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data

    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolios(self):
        """Returns the user's portfolio data """

        req = self.session.get(endpoints.portfolios(), timeout=15)
        req.raise_for_status()

        return req.json()['results'][0]

    @login_required
    def order_history(self, orderId=None):
        """Wrapper for portfolios
            Optional Args: add an order ID to retrieve information about a single order.
            Returns:
                (:obj:`dict`): JSON dict from getting orders
        """

        return self.session.get(endpoints.orders(orderId), timeout=15).json()

    def dividends(self):
        """Wrapper for portfolios
            Returns:
                (:obj: `dict`): JSON dict from getting dividends
        """

        return self.session.get(endpoints.dividends(), timeout=15).json()

    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data
            Returns:
                (:object: `dict`): JSON dict from getting positions
        """

        return self.session.get(endpoints.positions(), timeout=15).json()

    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in
            Returns:
                (:object: `dict`): Non-zero positions
        """

        return self.session.get(endpoints.positions() + '?nonzero=true', timeout=15).json()

    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################

    def place_order(self,
                    instrument,
                    quantity=1,
                    price=0.0,
                    transaction=None,
                    trigger='immediate',
                    order='market',
                    time_in_force='gfd'):
        """Place an order with Robinhood
            Notes:
                OMFG TEST THIS PLEASE!
                Just realized this won't work since if type is LIMIT you need to use "price" and if
                a STOP you need to use "stop_price".  Oops.
                Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order
            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                price (float): bid_price for order
                transaction (:enum:`Transaction`): BUY or SELL enum
                trigger (:enum:`Trigger`): IMMEDIATE or STOP enum
                order (:enum:`Order`): MARKET or LIMIT
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or until cancelled)
            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        if isinstance(transaction, str):
            transaction = Transaction(transaction)

        if not price:
            price = self.quote_data(instrument['symbol'])['bid_price']

        payload = {
            'account': self.get_account()['url'],
            'instrument': unquote(instrument['url']),
            'quantity': quantity,
            'side': transaction.name.lower(),
            'symbol': instrument['symbol'],
            'time_in_force': time_in_force.lower(),
            'trigger': trigger,
            'type': order.lower()
        }

        if order.lower() == "stop":
            payload['stop_price'] = float(price)
        else:
            payload['price'] = float(price)

        res = self.session.post(endpoints.orders(), data=payload, timeout=15)
        res.raise_for_status()

        return res

    def submit_order(self,
                     instrument_URL=None,
                     symbol=None,
                     order_type=None,
                     time_in_force=None,
                     trigger=None,
                     price=None,
                     stop_price=None,
                     quantity=None,
                     side=None):
        """Submits order to Robinhood
            Notes:
                This is normally not called directly.  Most programs should use
                one of the following instead:
                    place_market_buy_order()
                    place_limit_buy_order()
                    place_stop_loss_buy_order()
                    place_stop_limit_buy_order()
                    place_market_sell_order()
                    place_limit_sell_order()
                    place_stop_loss_sell_order()
                    place_stop_limit_sell_order()
            Args:
                instrument_URL (str): the RH URL for the instrument
                symbol (str): the ticker symbol for the instrument
                order_type (str): 'MARKET' or 'LIMIT'
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or
                                                       until cancelled)
                trigger (str): IMMEDIATE or STOP enum
                price (float): The share price you'll accept
                stop_price (float): The price at which the order becomes a
                                    market or limit order
                quantity (int): The number of shares to buy/sell
                side (str): BUY or sell
            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        # Used for default price input
        # Price is required, so we use the current bid price if it is not specified
        current_quote = self.get_quote(symbol)
        current_bid_price = current_quote['bid_price']

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(ValueError('Neither instrument_URL nor symbol were passed to submit_order'))
            for result in self.instruments(symbol):
                if result['symbol'].upper() == symbol.upper() :
                    instrument_URL = result['url']
                    break
            if(instrument_URL is None):
                raise(ValueError('instrument_URL could not be defined. Symbol %s not found' % symbol))

        if(symbol is None):
            symbol = self.session.get(instrument_URL, timeout=15).json()['symbol']

        if(side is None):
            raise(ValueError('Order is neither buy nor sell in call to submit_order'))

        if(order_type is None):
            if(price is None):
                if(stop_price is None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(ValueError('Invalid order_type in call to submit_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(ValueError('Limit order has no price in call to submit_order'))
            if(price <= 0):
                raise(ValueError('Price must be positive number in call to submit_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(ValueError('Stop order has no stop_price in call to submit_order'))
            if(stop_price <= 0):
                raise(ValueError('Stop_price must be positive number in call to submit_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(ValueError('Stop price set for non-stop order in call to submit_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(ValueError('Limit order has no price in call to submit_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(ValueError('Market order has price limit in call to submit_order'))
            price = float(price)
        else:
            price = current_bid_price # default to current bid price

        if(quantity is None):
            raise(ValueError('No quantity specified in call to submit_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(ValueError('Quantity must be positive number in call to submit_order'))

        payload = {}

        for field, value in [
                ('account', self.get_account()['url']),
                ('instrument', instrument_URL),
                ('symbol', symbol),
                ('type', order_type),
                ('time_in_force', time_in_force),
                ('trigger', trigger),
                ('price', price),
                ('stop_price', stop_price),
                ('quantity', quantity),
                ('side', side)
            ]:
            if(value is not None):
                payload[field] = value

        print(payload)

        res = self.session.post(endpoints.orders(), data=payload, timeout=15)
        res.raise_for_status()

        return res

    ############################################################
    #                          CANCEL ORDER
    ############################################################

    def cancel_order(self, order_id):
        """
        Cancels specified order and returns the response (results from `orders` command).
        If order cannot be cancelled, `None` is returned.
        Args:
            order_id (str or dict): Order ID string that is to be cancelled or open order dict returned from
            order get.
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        if isinstance(order_id, str):
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id
                                 + '\n Error message: ' + repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    raise ValueError('Failed to cancel order ID: ' + order_id
                                     + '\n Error message: ' + repr(err_msg))
                    return None

        if isinstance(order_id, dict):
            order_id = order_id['id']
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id
                                 + '\n Error message: ' + repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    raise ValueError('Failed to cancel order ID: ' + order_id
                                     + '\n Error message: ' + repr(err_msg))
                    return None

        elif not isinstance(order_id, str) or not isinstance(order_id, dict):
            raise ValueError('Cancelling orders requires a valid order_id string or open order dictionary')


        # Order type cannot be cancelled without a valid cancel link
        else:
            raise ValueError('Unable to cancel order ID: ' + order_id)

    ############################################################
    #                          CRYPTO
    ############################################################

    def get_crypto_quotes(self, currency_pair_ids=None, symbols=None):
        """Fetch stock quote
                    Args:
                        stock (str): stock ticker, prompt if blank
                    Returns:
                        (:obj:`dict`): JSON contents from `quotes` endpoint
                """

        url = None
        if currency_pair_ids:
            ids = ','.join(currency_pair_ids)
            url = str(endpoints.crypto_quote()) + "?ids=" + ids

        if symbols:
            symbols = ','.join(symbols)
            url = str(endpoints.crypto_quote()) + "?symbols=" + symbols

        # Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data

    def get_crypto_currency_pairs(self):
        url = str(endpoints.get_crypto_currency_pairs())

        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()

        return data['results']

    def get_crypto_historicals(self, currency_pair_id, interval, span=None, bounds=None):
        """
        Example response:
        {
            "open_price": "6767.5400",
            "span": "day",
            "symbol": "BTCUSD",
            "previous_close_price": "6767.5400",
            "interval": "5minute",
            "id": "3d961844-d360-45fc-989b-f6fca761d511",
            "data_points": [
                {
                    "open_price": "6586.0400",
                    "volume": "0.0000",
                    "begins_at": "2018-04-06T13:30:00Z",
                    "session": "reg",
                    "low_price": "6572.7050",
                    "interpolated": false,
                    "close_price": "6590.4750",
                    "high_price": "6596.7200"
                },
                {
                    "open_price": "6586.0150",
                    "volume": "0.0000",
                    "begins_at": "2018-04-06T13:35:00Z",
                    "session": "reg",
                    "low_price": "6579.1450",
                    "interpolated": false,
                    "close_price": "6587.2850",
                    "high_price": "6594.2450"
                },
                ...
            ],
            "bounds": "regular",
            "open_time": "2018-04-06T13:30:00Z",
            "previous_close_time": "2018-04-05T20:00:00Z"
        }
        """

        historicals_url = endpoints.crypto_historicals() + currency_pair_id + "/?interval=" + interval.value.lower() + "&span=" + span.value.lower() + "&bounds=" + bounds.value.lower()
        res = self.session.get(historicals_url, timeout=15)

        return res.json()
