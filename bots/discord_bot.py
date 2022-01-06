from datetime import time
import sys
import os
import base64
import json

import discord
from discord.ext import commands, tasks
from decouple import config as cfg

import stocktwits_bot
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")
from common import utils, constants, ticker_utils
from servers import keep_alive
from brokers import robinhood_client
import yahoo_finance_data as yfd


bot = commands.Bot(command_prefix = "!")
config = utils.load_config()
# st_bot = stocktwits_bot.StocktwitsBot()
# robinhood_client = robinhood_client.RobinhoodClient()
# previous_trending_list = None
discord_group = constants.ATLAS_TRADING

got_new_mentions_for_start_of_day = False
total_ticker_count_map = {}


@bot.event
async def on_ready():
    print("Now logged in as " + str(bot.user))
    # get_trending_information.start()
    get_discord_channel_ticker_mentions.start()
    # get_intraday_watchlist_info.start()
    

@tasks.loop(minutes = 15)
# @tasks.loop(seconds = 10)
async def get_trending_information():
    global previous_trending_list

    channel_id = discord_config["general_channel_id"]
    channel = bot.get_channel(channel_id)

    trending_tickers = st_bot.get_trending_tickers()

    timestamp = utils.get_timestamp()
    message = timestamp + "\n"
    exit_trending = set()
    new_trending = set()

    if previous_trending_list is not None:
        exit_trending = set(previous_trending_list) - set(trending_tickers)
        new_trending = set(trending_tickers) - set(previous_trending_list)
        
    
    for ticker in trending_tickers:
        message += ticker
        if ticker in new_trending:
            message += " <<"

        message += "\n"

    for ticker in exit_trending:
        message += ticker + " >>\n"

    print(message)

    await channel.send(message)
    
    previous_trending_list = trending_tickers


@tasks.loop(minutes = 1)
async def get_intraday_watchlist_info():
    channel_id = discord_config["general_channel_id"]
    channel = bot.get_channel(channel_id)
    timestamp = utils.get_timestamp()
    message = timestamp + "\n"
    watchlist_tickers = robinhood_client.get_watchlist_tickers(constants.INTRADAY_WATCHLIST)

    yfm = yfd.YahooFinanceModule(watchlist_tickers)
    yfm.get_daily_history()

    for ticker in watchlist_tickers:
        daily_percentage_change = yfm.get_daily_percentage_change(ticker)
        ticker_str = ticker + " -- " + daily_percentage_change + "% -- " + "\n"
        message += ticker_str

    await channel.send(message)


@tasks.loop(minutes = 5)
async def get_discord_channel_ticker_mentions():
    global got_new_mentions_for_start_of_day
    global total_ticker_count_map

    channel_id = discord_config["channels"][constants.PERSONAL_SERVER]["channel_id"]
    channel = bot.get_channel(channel_id)
    time_now_hours = utils.get_time_hours()
    time_now_hours = int(time_now_hours)
    message = ""

    if time_now_hours >= 9 and time_now_hours <= 21:
        timestamp = utils.get_timestamp()
        print("Market hours, currently: " + timestamp)
        if not got_new_mentions_for_start_of_day:
            print("Start of day: getting mentions since pre-market open!")
            start_time = constants.PREMARKET_START
        else:
            start_time = utils.get_date_minutes_before()

        end_time = utils.get_time()
        print("Start time: " + str(start_time))
        print("End time: " + str(end_time))
        ticker_count_map = get_ticker_mentions(discord_group, start_time, end_time)
        

        timestamp = utils.get_timestamp()
        message = ""
        new_mentions = []

        for ticker in ticker_count_map:
            ticker_count = ticker_count_map[ticker]
            if not got_new_mentions_for_start_of_day and ticker_count < 3:
                continue
            
        
            if ticker not in total_ticker_count_map:
                new_mentions.append((ticker, ticker_count))
                # print("Added " + ticker)
            else:
                total_count = ticker_count + total_ticker_count_map[ticker]
                message += ticker + "+" + str(ticker_count) + " => " + str(total_count)  + "\n"

            if ticker not in total_ticker_count_map:
                total_ticker_count_map[ticker] = ticker_count
            else:
                total_ticker_count_map[ticker] += ticker_count

        # total_ticker_count_map.update(ticker_count_map)

        if len(new_mentions) != 0:
            new_mention_str = "New mentions:\n"

            for new_mention in new_mentions:
                ticker = new_mention[0]
                ticker_count = new_mention[1]
                addend = ticker
                if new_mention[1] > 1:
                    addend += " (" + str(ticker_count) + ")"
                addend += ", "
                new_mention_str += addend

            message = new_mention_str + message + "\n"

        message = "--------" + timestamp + "--------\n" + message
        message += "--------------------"

        print(message)

        if not got_new_mentions_for_start_of_day:
            got_new_mentions_for_start_of_day = True

        await channel.send(message)

    elif time_now_hours >= 20:
        got_new_mentions_for_start_of_day = False
        total_ticker_count_map.clear()
        print("Past market hours, nothing to send")


def get_ticker_mentions(discord_group, start_time, end_time):
    discord_chat_exporter_dll_file_path = "../../" + config["discord_exporter_cli"]["dll_file_directory"]
    discord_token = discord_config["channels"][discord_group]["cli_token"]
    discord_channel_id = discord_config["channels"][discord_group]["channel_id"]
    date_today = utils.get_date_today()
    after_time = date_today + " " + start_time
    end_time = utils.get_time()
    before_time = date_today + " " + end_time
    time_range = start_time + "_to_" + end_time
    
    output_directory = "../" + config["discord_exporter_cli"]["output_directory"]
    output_directory = output_directory.replace("${discord_group_name}", discord_group)
    output_directory = output_directory.replace("${date_timestamp}", date_today)
    output_directory = output_directory.replace("${timestamp}", time_range)
    utils.make_directory(output_directory)
    filename = discord_group + "_" + date_today + "--" + time_range
    output_file_path = output_directory + "/" + filename + ".json"
    
    
    cmd = "dotnet "
    cmd += discord_chat_exporter_dll_file_path + " export"
    cmd += " -t " + discord_token 
    cmd += " -c " + str(discord_channel_id)
    cmd += " --after \"" + after_time + "\""
    cmd += " --before \"" + before_time + "\""
    cmd += " -o " + "\"" + output_file_path + "\""
    cmd += " -f Json"

    # print("Command to get discord mentions:\n" + cmd)

    status, output = utils.execute_cmd(cmd)

    # print("Finished generating the JSON output for discord messages from " + after_time + " to " + before_time + "!")

    discord_messages_json = json.load(open(output_file_path))
    discord_messages = discord_messages_json["messages"]
    ticker_count_map = ticker_utils.get_ticker_count(discord_messages)

    ticker_count_map = {k: v for k, v in sorted(ticker_count_map.items(), key=lambda item: item[1])}

    # Cache ticker_count_map in data store
    data_output_directory = "../" + config["data_directory"]["discord_ticker_mentions"]
    data_output_directory = data_output_directory.replace("${discord_group_name}", discord_group)
    data_output_directory = data_output_directory.replace("${date_timestamp}", date_today)
    data_output_directory = data_output_directory.replace("${timestamp}", time_range)
    data_filename = "discord_messages_ticker_data_" + filename + ".json"
    utils.save_json(ticker_count_map, data_output_directory, data_filename)

    return ticker_count_map










if __name__ == '__main__':
    discord_config = base64.b64decode(cfg(constants.DISCORD_SECRET_KEYNAME))
    discord_config = json.loads(discord_config)["discord_secrets"]
    encoded_token = discord_config["channels"][constants.PERSONAL_SERVER]["oauth_token"]
    decoded_token = base64.b64decode(encoded_token)
    token_json = json.loads(decoded_token)
    token = token_json["access_token"]
    keep_alive.keep_alive()
    got_new_mentions_for_start_of_day = False
    bot.run(token)
    robinhood_client.logout()





