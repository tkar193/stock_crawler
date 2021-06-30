import json
import re
import datetime
import argparse
import sys
import os

import praw
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")

from common import utils, constants


args = None
config = None



def trim_post_title(post_title):
    post_title = re.sub('[!,*)@#%(&$_?.^]', "", post_title)
    post_title = post_title.replace("'s", "")

    return post_title


def arg_parser():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type_of_post', nargs='?', type=str, default = None, help = "Either 'new' or 'hot'")
    parser.add_argument('-s', '--subreddit', nargs='?', type=str, default = None, help = "Enter a subreddit name, i.e.:  investing, algotrading, wallstreetbets, pennystocks, robinhood")
    args = parser.parse_args()



if __name__ == '__main__':
    arg_parser()
    type_of_post = args.type_of_post
    subreddit = args.subreddit

    config = utils.load_config()
    path_to_tickers_data = "../" + config["data_directory"]["ticker_list"]
    path_to_ticker_ignore = "../" + config["data_directory"]["ticker_ignore"]

    config = config["reddit"]
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    username = config["username"]
    password = config["password"]
    user_agent = config["user_agent"]

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent)

    tickers_pd = pd.read_csv(path_to_tickers_data)
    ticker_ignore_pd = pd.read_csv(path_to_ticker_ignore)
    ticker_set = tickers_pd["Symbol"].unique()
    ticker_ignore_set = ticker_ignore_pd["Symbol"].unique()
    ticker_count_map = {}

    # wsb_subreddit = reddit.subreddit(constants.WALLSTREETBETS_SUBREDDIT_NAME)
    wsb_subreddit = reddit.subreddit(subreddit)
    if type_of_post == "new":
        wsb = wsb_subreddit.new(limit=constants.POST_LIMIT)
    elif type_of_post == "hot":
        wsb = wsb_subreddit.hot(limit=constants.POST_LIMIT)

    for submission in wsb:
        if submission.stickied:
            continue

        flair = submission.link_flair_text
        created_date = submission.created_utc
        created_date = datetime.datetime.fromtimestamp(created_date)
        post_title = trim_post_title(submission.title)

        if flair is None:
            flair = "NO FLAIR"
        print(flair + " --- " + str(created_date) + " --- " + post_title)

        for word in post_title.split():
            if word.lower() == word and word.upper() in ticker_set:
                continue

            if word.upper() in ticker_set:
                ticker = word.upper()

                if ticker in ticker_ignore_set:
                    continue

                if ticker not in ticker_count_map.keys():
                    ticker_count_map[ticker] = 0

                ticker_count_map[ticker] += 1
                print("    TICKER: $" + word.upper())

    ticker_count_map = {k: v for k, v in sorted(ticker_count_map.items(), key=lambda item: item[1])}

    tickers = list(ticker_count_map.keys())
    ticker_count = list(ticker_count_map.values())

    for ticker in ticker_count_map.keys():
        count = ticker_count_map[ticker]
        print(ticker + ": " + str(count))

    for i in range(len(tickers)):
        if ticker_count[i] > 1:
            cutoff_i = i
            break

    tickers = tickers[cutoff_i:]
    ticker_count = ticker_count[cutoff_i:]

    fig, ax = plt.subplots()
    ax.barh(tickers, ticker_count)
    ax.tick_params(axis='both', which='major',
                   labelsize=constants.SMALL_FONT_SIZE)
    ax.tick_params(axis='both', which='minor',
                   labelsize=constants.SMALL_FONT_SIZE)
    plt.show()
