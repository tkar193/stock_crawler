import json
import subprocess
import sys
import os
import datetime
import hashlib

import pandas as pd


sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(".")

import constants


### GENERAL COMMANDS



def load_config(application=None):
    path_to_config = constants.LOCAL_ABSOLUTE_PROJECT_DIRECTORY_PREFIX + "/config/config.json"

    with open(path_to_config, "r") as config_file:
        try:
            config = json.loads(config_file.read())
            if application is not None:
                config = config[application]
        except Exception as e:
            raise Exception("Could not read config.json: " + str(e))

    return config


def pretty_print(json_object):
    print(json.dumps(json_object, indent=4, sort_keys=True))


def execute_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    status = process.wait()

    if status != 0:
        output = error

    return status, output



### DATETIME COMMANDS

def get_timestamp(get_whole_timestamp = False):
    now = str(datetime.datetime.now())[:-3]
    if not get_whole_timestamp:
        now = now.split(".")[0]
        now = now[:-3]
        now = now.replace(" ", "T")
    return now


def get_date_today():
    date_today = datetime.date.today()
    return date_today

def get_date_yesterday():
    date_yesterday = get_date_today() - datetime.timedelta(days=1)
    return date_yesterday


### SECURITY COMMANDS


def get_sha256_hash():
    pass



### DATA COMMANDS

def import_ticker_symbol_data():
    config = load_config()
    path_to_tickers_data = config["data_directory"]["ticker_list"]
    tickers_pd = pd.read_csv(path_to_tickers_data)

    # tickers = tickers_pd["Symbol"]
    ticker_list = tickers_pd["Symbol"].values.tolist()

    return ticker_list


### STRING COMMANDS

def list_to_comma_separated_string(ticker_list):
    ticker_list_str = ""

    for ticker in ticker_list:
        ticker_list_str += ticker + ","

    ticker_list_str = ticker_list_str[:-1]

    return ticker_list_str


### MATH COMMANDS

def get_daily_percentage_change(previous_close, close):
    daily_percentage_change = (float(close) - float(previous_close)) / float(previous_close)
    daily_percentage_change = daily_percentage_change * 100
    daily_percentage_change = str(round(daily_percentage_change, 2))
    return daily_percentage_change



# ticker_list = import_ticker_symbol_data()
# t = get_date_today()
# y = get_date_yesterday()
# print(y)