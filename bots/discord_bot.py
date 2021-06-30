import sys
import os
import base64
import json

import discord
from discord.ext import commands, tasks

import stocktwits_bot

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")

from common import utils, constants
from servers import keep_alive


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
previous_trending_list = None


@bot.event
async def on_ready():
    get_trending_information.start()
    print("Are now logged in as " + str(bot.user))

# @tasks.loop(minutes = 15)
@tasks.loop(seconds = 30)
async def get_trending_information():
    global previous_trending_list

    channel_id = discord_config["general_channel_id"]
    channel = bot.get_channel(channel_id)

    trending_tickers = st_bot.get_trending_tickers()

    timestamp = utils.get_timestamp()
    message = timestamp + "\n" + str(trending_tickers) + "\n"
    
    if previous_trending_list is not None:
        exit_trending = set(previous_trending_list) - set(trending_tickers)
        new_trending = set(trending_tickers) - set(previous_trending_list)
        if exit_trending != set():
            message += "Tickers exiting trending: " + str(exit_trending) + "\n"
        if new_trending != set():
            message += "Tickers entering trending: " + str(new_trending) + "\n"

    print(message)

    await channel.send(message)
    
    previous_trending_list = trending_tickers
    


if __name__ == '__main__':
    discord_config = utils.load_config(application = "discord")
    encoded_token = discord_config["token"]
    decoded_token = base64.b64decode(encoded_token)
    token_json = json.loads(decoded_token)
    token = token_json["access_token"]
    keep_alive.keep_alive()
    bot.run(token)





