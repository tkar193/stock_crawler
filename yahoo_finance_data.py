import json
import argparse

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


def arg_parser():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--ticker', nargs='?', type=str, default = None)

    args = parser.parse_args()


if __name__ == '__main__':
    arg_parser()
    ticker = args.ticker

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    configure_plot_settings()

    ticker_data = yf.Ticker(ticker)
    ticker_df = ticker_data.history(period="1h", interval="15m", start="2021-5-01")
    add_moving_averages(ticker_df)

    dates = ticker_df.index
    dates = list(dates)
    for i in range(len(dates)):
        if i % 26 != 0:
            dates[i] = ""
        else:
            dates[i] = str(dates[i])
            dates[i] = dates[i].split(" ")[0]

    num_dates = len(dates)
    
    closing_prices = ticker_df["Close"]
    hourly_volume = ticker_df["Volume"]

    sma_short_str = "SMA_" + str(constants.SHORT_SMA)
    sma_long_str = "SMA_" + str(constants.LONG_SMA)
    vma_str = "VMA_" + str(constants.VOLUME_MA)
    sma_short = ticker_df[sma_short_str]
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
