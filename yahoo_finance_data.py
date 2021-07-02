import json
import argparse
import time

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from common import utils, constants


args = None

fig = None
ax1 = None
ax2 = None



def configure_plot_settings():
    global fig
    global ax1
    global ax2

    # fig = plt.figure(figsize=(8, 5))
    # ax1 = plt.subplot(1, 1, 1)
    # ax2 = ax1.twinx()
    # plt.rcParams['figure.figsize'] = (20, 10)
    # fig, ax1 = plt.subplots()


def add_moving_averages(ticker_df):

    SMAs = [constants.SHORT_SMA, constants.LONG_SMA]

    for sma in SMAs:
        sma_str = "SMA_" + str(sma)
        ticker_df[sma_str] = ticker_df.iloc[:,3].rolling(window = sma).mean()

    vma_str = "VMA_" + str(constants.VOLUME_MA)

    ticker_df[vma_str] = ticker_df.iloc[:,4].rolling(window = constants.VOLUME_MA).mean()


class YahooFinanceModule():

    def __init__(self, ticker_list, period, interval, start, end = None):
        self.ticker_list = ticker_list
        self.period = period
        self.interval = interval
        self.start = start
        self.end = end


        self.ticker_list_str = utils.list_to_comma_separated_string(ticker_list)
        # self.ticker_data = yf.Tickers(self.ticker_list_str)
        # print(self.ticker_data.tickers.keys())
        self.__map_ticker_to_number()
        self.ticker_df = None


    def get_history(self, do_split = False):
        
        # Split up all 7000+ tickers in 7 parts of 1000 tickers each
        
        i = 0
        # constants.LENGTH_GET_HISTORY_WINDOW
        max_num_tickers = len(self.ticker_list)
        print("Max number of tickers: " + str(max_num_tickers))

        ticker_dfs = []

        self.ticker_df = None

        if do_split:
            while i < max_num_tickers:
                i_next = min(i + constants.LENGTH_GET_HISTORY_WINDOW, max_num_tickers - 1)

                print("Getting tickers " + str(i) + ": " + self.ticker_list[i] + " to " + str(i_next) + ": " + self.ticker_list[i_next])
                ticker_list_subset = self.ticker_list[i:i_next]
                print(ticker_list_subset)
                ticker_list_subset_str = utils.list_to_comma_separated_string(ticker_list_subset)
                ticker_data_subset = yf.Tickers(ticker_list_subset_str)
                ticker_df_subset = ticker_data_subset.history(period = self.period, interval = self.interval, start = self.start)
                ticker_dfs.append(ticker_df_subset)

                i += constants.LENGTH_GET_HISTORY_WINDOW

                print(str(i_next) + " TICKERS PROCESSED")

                if self.ticker_df is None:
                    self.ticker_df = ticker_df_subset
                else:
                    self.ticker_df = pd.concat([self.ticker_df, ticker_df_subset])
        else:
            self.ticker_data = yf.Tickers(self.ticker_list_str)
            self.ticker_df = self.ticker_data.history(period = self.period, interval = self.interval, start = self.start)
        
        print("Got the history... now adding moving averages: " + utils.get_timestamp(get_whole_timestamp = True))
        self.__add_moving_averages()
        print("Just got the moving averages: " + utils.get_timestamp(get_whole_timestamp = True))


    def plot_ticker_chart(self, ticker):
        
        try:
            ticker_df = self.ticker_df.loc[:, (slice(None), ticker)]
        except Exception as e:
            ticker_data = yf.Ticker(ticker)
            ticker_df = ticker_data.history(period=self.period, interval=self.interval, start = self.start)

        # add_moving_averages(ticker_df)

        dates = ticker_df.index
        dates = list(dates)
        for i in range(len(dates)):
            if i % 26 != 0:
                dates[i] = ""
            else:
                dates[i] = str(dates[i])
                dates[i] = dates[i].split(" ")[0]

        num_dates = len(dates)
        
        closing_prices = ticker_df["Close"][ticker]
        # print(closing_prices)
        hourly_volume = ticker_df["Volume"][ticker]

        sma_short_str = "SMA_" + str(constants.SHORT_SMA)
        sma_long_str = "SMA_" + str(constants.LONG_SMA)
        vma_str = "VMA_" + str(constants.VOLUME_MA)
        sma_short = ticker_df[sma_short_str]
        print(sma_short)
        sma_long = ticker_df[sma_long_str]
        vma = ticker_df[vma_str]

        idx = np.array(range(num_dates))
        plt.xticks(idx, dates)
        plt.plot(idx, closing_prices)
        plt.plot(idx, sma_short, label = sma_short_str)
        plt.plot(idx, sma_long, label = sma_long_str)
        ax1 = plt.gca()
        plt.draw()
        ax1.set_xticklabels(dates, rotation=constants.XTICK_ROTATION)
        ax1.set_ylim(0, closing_prices.max() * 1.25)

        ax2 = ax1.twinx()
        plt.bar(idx, hourly_volume, color="red")
        plt.plot(idx, vma)
        ax2.set_xticklabels(dates, rotation=90)
        ax2.set_ylim(0, hourly_volume.max() * 8)

        plt.show()



    def  __add_moving_averages(self):
        SMAs = [constants.SHORT_SMA, constants.LONG_SMA]
        N = len(self.ticker_list)

        for ticker in self.ticker_list:
            i = self.ticker_map[ticker]
            
            for sma in SMAs:
                sma_str = "SMA_" + str(sma)
                self.ticker_df[(sma_str, ticker)] = self.ticker_df.iloc[:,i+N*constants.TICKERS_CLOSING_INDEX].rolling(window = sma).mean()

            vma_str = "VMA_" + str(constants.VOLUME_MA)

            self.ticker_df[(vma_str, ticker)] = self.ticker_df.iloc[:,i+N*constants.TICKERS_VOLUME_INDEX].rolling(window = constants.VOLUME_MA).mean()


    def __map_ticker_to_number(self):
        self.ticker_map = {}

        i = 0
        for ticker in self.ticker_list:
            self.ticker_map[ticker] = i
            i += 1


def arg_parser():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--ticker', nargs='?', type=str, default = None, ticker = None)

    args = parser.parse_args()


if __name__ == '__main__':
    # arg_parser()
    # ticker = args.ticker

    # ticker = "AAPL"
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # tickers = utils.import_ticker_symbol_data()
    tickers = ["AMC", "WISH", "STAF", "JOB", "MRIN"]
    period = "1h"
    interval = "1h"
    start = "2021-6-01"
    yfm = YahooFinanceModule(tickers, period, interval, start)
    

    print("Now getting history: " + utils.get_timestamp(get_whole_timestamp = True))
    yfm.get_history()
    print("Got the history: " + utils.get_timestamp(get_whole_timestamp = True))

    yfm.plot_ticker_chart("AMC")
    

    