import sys
import os

import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")
from common import utils, constants


yf.pdr_override() # <== that's all it takes :-)


ticker_list = ["MSFT", "TSLA", "AAPL"]
period = "1h"
interval = "1h"
start = "2021-06-01"
# ticker_list = utils.import_ticker_symbol_data()
ticker_list_str = utils.list_to_comma_separated_string(ticker_list)
print(ticker_list_str)
data = yf.Tickers(ticker_list_str)
ticker_df = data.history(period = period, interval = interval, start = start)

print(ticker_df.loc[:, (slice(None), "AAPL")])


