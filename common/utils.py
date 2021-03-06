import json
import subprocess
import sys
import os
import datetime
import calendar
from pytz import timezone
import time

import pandas as pd


sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(".")

import constants


### GENERAL COMMANDS



def load_config(application=None):
    path_to_config = "../config/config.json"

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

def make_directory(output_directory):
    try:
        os.makedirs(output_directory)
        # print("Output directory created at: " + output_directory)
    except Exception as e:
        print("Exception when trying to create output directory " + output_directory + ": " + str(e))


def save_json(to_json, output_directory, filename):
    make_directory(output_directory)
    output_file_path = output_directory + "/" + filename
    with open(output_file_path, "w") as outfile:
        json.dump(to_json, outfile)
    print("Saved json data to " + output_file_path)

### DATETIME COMMANDS

tz = timezone("EST")

def get_timestamp(get_whole_timestamp = False):
    now = str(datetime.datetime.now(tz))[:-3]
    if not get_whole_timestamp:
        now = now.split(".")[0]
        now = now[:-3]
        now = now.replace(" ", "T")
    return now

def get_time():
    now = str(datetime.datetime.now(tz))[:-3]
    now = now.split(".")[0]
    now = now[:-3]
    now = now.split(" ")[1]
    return now

def get_time_hours():
    return get_time().split(":")[0]

def get_date_today():
    # date_today = str(datetime.date.today())
    date_today = str(datetime.datetime.now(tz))
    date_today = date_today.split(" ")[0]
    return date_today

def get_date_yesterday(num_days = 1):
    date_yesterday = str(datetime.date.today() - datetime.timedelta(days = num_days))
    return date_yesterday

def get_day_today():
    curr_date = datetime.date.today()
    day = calendar.day_name[curr_date.weekday()]
    return day

def is_weekday():
    day = get_day_today()
    if day in ["Saturday", "Sunday"]:
        return False
    else:
        return True
    

def get_date_minutes_before(num_minutes = 5):
    time_before = str(datetime.datetime.now(tz) - datetime.timedelta(minutes = num_minutes))
    time_before = time_before.split(".")[0]
    time_before = time_before[:-3]
    time_before = time_before.split(" ")[1]
    return time_before


def get_time_unix():
    t = time.time()
    t = str(t)
    t = t.split(".")[0]
    t = int(t)
    return t


def get_time_unix_from_date(date):
    date_format = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M")
    unix_time = datetime.datetime.timestamp(date_format)
    unix_time = str(unix_time).split(".")[0]
    unix_time = int(unix_time)
    return unix_time


def get_market_start_time():
    date_today = str(datetime.datetime.now(tz))
    date_today = date_today.split(" ")[0]
    date_today += "T09:00"
    return date_today





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

def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)



# t = get_date_today()
# print(t)
# y = get_date_yesterday()
# print(y)
# t = get_date_today()
# print(t)
# t = get_date_minutes_before()
# print(t)
# t = get_timestamp()
# print(t)
# t = get_time_unix_from_date(t)
# print(t)
# t_now = get_time_unix()
# print(t_now)
# t = get_time_unix()
# print(t)
# t = get_market_start_time()
# print(t)
