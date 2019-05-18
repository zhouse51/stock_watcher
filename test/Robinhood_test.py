from robinhood.Robinhood import Robinhood, Transaction
import time
import datetime


def place_buy_order(rb,
                    instrument,
                    quantity,
                    bid_price=0.0):
    """Wrapper for placing buy orders
        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """

    transaction = Transaction.BUY

    return rb.place_order(instrument, quantity, bid_price, transaction)


def place_sell_order(rb,
                     instrument,
                     quantity,
                     bid_price=0.0):
    """Wrapper for placing sell orders
        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """

    transaction = Transaction.SELL

    return rb.place_order(instrument, quantity, bid_price, transaction)


    # Methods below here are a complete rewrite for buying and selling
    # These are new. Use at your own risk!

def place_market_buy_order(rb,
                           instrument_URL=None,
                           symbol=None,
                           time_in_force=None,
                           quantity=None):
    """Wrapper for placing market buy orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            quantity (int): Number of shares to buy
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='market',
                             trigger='immediate',
                             side='buy',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             quantity=quantity))


def place_limit_buy_order(rb,
                          instrument_URL=None,
                          symbol=None,
                          time_in_force=None,
                          price=None,
                          quantity=None):
    """Wrapper for placing limit buy orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            price (float): The max price you're willing to pay per share
            quantity (int): Number of shares to buy
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='limit',
                             trigger='immediate',
                             side='buy',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             price=price,
                             quantity=quantity))


def place_stop_loss_buy_order(rb,
                              instrument_URL=None,
                              symbol=None,
                              time_in_force=None,
                              stop_price=None,
                              quantity=None):
    """Wrapper for placing stop loss buy orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            stop_price (float): The price at which this becomes a market order
            quantity (int): Number of shares to buy
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='market',
                             trigger='stop',
                             side='buy',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             stop_price=stop_price,
                             quantity=quantity))


def place_stop_limit_buy_order(rb,
                               instrument_URL=None,
                               symbol=None,
                               time_in_force=None,
                               stop_price=None,
                               price=None,
                               quantity=None):
    """Wrapper for placing stop limit buy orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            stop_price (float): The price at which this becomes a limit order
            price (float): The max price you're willing to pay per share
            quantity (int): Number of shares to buy
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='limit',
                             trigger='stop',
                             side='buy',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             stop_price=stop_price,
                             price=price,
                             quantity=quantity))

def place_market_sell_order(rb,
                            instrument_URL=None,
                            symbol=None,
                            time_in_force=None,
                            quantity=None):
    """Wrapper for placing market sell orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            quantity (int): Number of shares to sell
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='market',
                             trigger='immediate',
                             side='sell',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             quantity=quantity))

def place_limit_sell_order(rb,
                           instrument_URL=None,
                           symbol=None,
                           time_in_force=None,
                           price=None,
                           quantity=None):
    """Wrapper for placing limit sell orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            price (float): The minimum price you're willing to get per share
            quantity (int): Number of shares to sell
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='limit',
                             trigger='immediate',
                             side='sell',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             price=price,
                             quantity=quantity))

def place_stop_loss_sell_order(rb,
                               instrument_URL=None,
                               symbol=None,
                               time_in_force=None,
                               stop_price=None,
                               quantity=None):
    """Wrapper for placing stop loss sell orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            stop_price (float): The price at which this becomes a market order
            quantity (int): Number of shares to sell
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='market',
                             trigger='stop',
                             side='sell',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             stop_price=stop_price,
                             quantity=quantity))

def place_stop_limit_sell_order(rb,
                                instrument_URL=None,
                            symbol=None,
                                time_in_force=None,
                                price=None,
                                stop_price=None,
                                quantity=None):
    """Wrapper for placing stop limit sell orders
        Notes:
            If only one of the instrument_URL or symbol are passed as
            arguments the other will be looked up automatically.
        Args:
            instrument_URL (str): The RH URL of the instrument
            symbol (str): The ticker symbol of the instrument
            time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
            stop_price (float): The price at which this becomes a limit order
            price (float): The max price you're willing to get per share
            quantity (int): Number of shares to sell
        Returns:
            (:obj:`requests.request`): result from `orders` put command
    """
    return(rb.submit_order(order_type='limit',
                             trigger='stop',
                             side='sell',
                             instrument_URL=instrument_URL,
                             symbol=symbol,
                             time_in_force=time_in_force,
                             stop_price=stop_price,
                             price=price,
                             quantity=quantity))


rb = Robinhood()
if not rb.login(username="s0148897@gmail.com", password="April@1312"):
    print('Login failed.')
    exit()

print("quote_data")
data = rb.quote_data('ZM')
print(data)

print("investment_profile")
data = rb.investment_profile()
print(data)

print("historical_quotes")
data = rb.get_historical_quotes('ZM', '5minute', 'day')
print(data)

print("quote_list")
# possible keys
# 'ask_price','ask_size','bid_price','bid_size','last_trade_price','last_extended_hours_trade_price','previous_close','adjusted_previous_close','previous_close_date','symbol','trading_halted','has_traded','last_trade_price_source','updated_at','instrument'
data = rb.get_quote_list('ZM', 'symbol,ask_price,bid_price,last_trade_price')
print(data)
for item in data:
    quote_str = item[0] + ": ask $" + item[1] + ": bid $" + item[2] + ": trade $" + item[3]
    print(quote_str)

print("get_account")
data = rb.get_account()
print(data)

print("get_popularity")
data = rb.get_popularity('ZM')
print(data)

print("get_tickers_by_tag: top-movers")
data = rb.get_tickers_by_tag(tag='top-movers')
print(data)
print("get_tickers_by_tag: 100-most-popular")
data = rb.get_tickers_by_tag(tag='100-most-popular')
print(data)

print("get_transfers")
data = rb.get_transfers()
print(data)

print("get_options")
data = rb.get_options('ZM', '2019-04-10', 'put')
print(data)

print("get_fundamentals")
data = rb.get_fundamentals('ZM')
print(data)

print("portfolios")
data = rb.portfolios()
print(data)

print("order_history")
data = rb.order_history()
print(data)

print("dividends")
data = rb.dividends()
print(data)

print("positions")
data = rb.positions()
print(data)

print("securities_owned")
data = rb.securities_owned()
print(data)


rb.logout()
print("completed")
