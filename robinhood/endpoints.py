API_HOST = "https://api.robinhood.com"
NUMMUS_HOST = 'https://nummus.robinhood.com/'

def login():
    return API_HOST + "/oauth2/token/"


def logout():
    return API_HOST + "/oauth2/revoke_token/"


def investment_profile():
    return API_HOST + "/user/investment_profile/"


def accounts():
    return API_HOST + "/accounts/"


def ach(option):
    # Combination of 3 ACH endpoints. Options include:
    #     * iav
    #     * relationships
    #     * transfers
    return API_HOST + "/ach/iav/auth/" if option == "iav" else API_HOST + "/ach/{_option}/".format(_option=option)


def applications():
    return API_HOST + "/applications/"


def dividends():
    return API_HOST + "/dividends/"


def edocuments():
    return API_HOST + "/documents/"


def instruments(instrumentId=None, option=None):
    # Return information about a specific instrument by providing its instrument id.
    # Add extra options for additional information such as "popularity"
    return API_HOST + "/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")


def margin_upgrades():
    return API_HOST + "/margin/upgrades/"


def markets():
    return API_HOST + "/markets/"


def notifications():
    return API_HOST + "/notifications/"


def orders(orderId=None):
    return API_HOST + "/orders/" + ("{id}/".format(id=orderId) if orderId else "")


def password_reset():
    return API_HOST + "/password_reset/request/"


def portfolios():
    return API_HOST + "/portfolios/"


def positions():
    return API_HOST + "/positions/"


def quotes():
    return API_HOST + "/quotes/"


def historicals():
    return API_HOST + "/quotes/historicals/"


def rating():
    return API_HOST + "/midlands/ratings/"


def document_requests():
    return API_HOST + "/upload/document_requests/"


def user():
    return API_HOST + "/user/"


def watchlists():
    return API_HOST + "/watchlists/"


def news(stock):
    return API_HOST + "/midlands/news/{_stock}/".format(_stock=stock)


def fundamentals(stock):
    return API_HOST + "/fundamentals/{_stock}/".format(_stock=stock)


def tags(tag=None):
    # Returns endpoint with tag concatenated.
    return API_HOST + "/midlands/tags/tag/{_tag}/".format(_tag=tag)


def chain(instrumentid):
    return API_HOST + "/options/chains/?equity_instrument_ids={_instrumentid}".format(_instrumentid=instrumentid)


def options(chainid, dates, option_type):
    return API_HOST + "/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}".format(_chainid=chainid, _dates=dates, _type=option_type)


def market_data(optionid):
    return API_HOST + "/marketdata/options/{_optionid}/".format(_optionid=optionid)


def convert_token():
    return API_HOST + "/oauth2/migrate_token/"


def crypto_quote():
    return API_HOST + "/marketdata/forex/quotes/"


def get_crypto_currency_pairs():
    return NUMMUS_HOST + "/currency_pairs/"


def crypto_historicals():
    return API_HOST + "/marketdata/forex/historicals/"
