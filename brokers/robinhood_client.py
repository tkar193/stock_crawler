import os
import sys
import time
import base64
import json


from decouple import config
import robin_stocks.robinhood as rs

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")

from common import utils, constants


class RobinhoodClient():
    def __init__(self):
        login_credentials = base64.b64decode(config("ROBINHOOD_LOGIN_DETAILS"))
        login_credentials_json = json.loads(login_credentials)
        username = login_credentials_json["login_details"]["username"]
        password = login_credentials_json["login_details"]["password"]

        rs.login(username=username, password=password, expiresIn=86400, by_sms=True, store_session = False)

    def get_watchlist_tickers(self, watchlist_name):
        ticker_list = []

        growth_watchlist = rs.account.get_watchlist_by_name(name = watchlist_name)

        for ticker in growth_watchlist["results"]:
            symbol = ticker["symbol"]
            # print(ticker["symbol"])
            ticker_list.append(symbol)
            
        return ticker_list
        

    def logout(self):
        rs.logout()





if __name__ == '__main__':
    robinhood_client = RobinhoodClient()
    robinhood_client.get_watchlist_tickers(constants.INTRADAY_WATCHLIST)
    robinhood_client.logout()