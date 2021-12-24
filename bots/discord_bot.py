import sys
import os
import base64
import json

import discord
from discord.ext import commands, tasks
from decouple import config

import stocktwits_bot
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")
from common import utils, constants
from servers import keep_alive
from brokers import robinhood_client
import yahoo_finance_data as yfd


###### IGNORE ###########

class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.config = utils.load_config(application = "discord")
        

    async def on_ready(self):
        print("Are now logged in as " + str(self.user))


    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")


    def run(self):
        token = self.config["token"]
        super().run(token)

    
    def send_message(self):
        channel_name = "#general"
        channel = discord.utils.get(self.get_all_channels(), name = channel_name)
        print("Channel info: " + str(channel))
        channel_id = channel.id
        print("Channel id: " + channel_id)


###############


bot = commands.Bot(command_prefix = "!")
discord_config = utils.load_config(application = "discord")
st_bot = stocktwits_bot.StocktwitsBot()
robinhood_client = robinhood_client.RobinhoodClient()
previous_trending_list = None


@bot.event
async def on_ready():
    print("Are now logged in as " + str(bot.user))
    # get_trending_information.start()
    get_intraday_watchlist_info.start()
    

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



if __name__ == '__main__':
    discord_config = utils.load_config(application = "discord")
    encoded_token = discord_config["token"]
    decoded_token = base64.b64decode(encoded_token)
    token_json = json.loads(decoded_token)
    token = token_json["access_token"]
    keep_alive.keep_alive()
    bot.run(token)
    robinhood_client.logout()





