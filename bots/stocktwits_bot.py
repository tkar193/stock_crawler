import json
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")

from common import constants, utils

class StocktwitsBot():
    def __init__(self):
        self.config = utils.load_config()

    def get_trending_tickers(self):
        cmd = "curl -X GET "
        cmd += constants.STOCKTWITS_ENDPOINT + "/trending/symbols.json?access_token=<access_token>"

        access_token = self.config["stocktwits"]["access_token"]
        cmd = cmd.replace("<access_token>", access_token)

        # print("Command to get trending stocks: " + cmd)

        status, output = utils.execute_cmd(cmd)

        if status != 0:
            print("Failed request, output:\n" + output)

        # print("Output:\n" + output)

        trending_ticker_json = json.loads(output)

        # utils.pretty_print(trending_ticker_json)

        trending_tickers_list = []

        for item in trending_ticker_json["symbols"]:
            ticker = item["symbol"]
            # print(ticker)
            trending_tickers_list.append(ticker)

        return trending_tickers_list

    def save_trending_tickers(self):
        trending_tickers_list = self.get_trending_tickers()
        timestamp = utils.get_timestamp()
        output_dir = self.config["data_directory"]["stocktwits_trending"]
        output_dir = output_dir.replace("${datetime}", timestamp)
        output_filename = output_dir + ".json"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(trending_tickers_list, f, ensure_ascii = False, indent = 4)

        return trending_tickers_list
        
        


        





if __name__ == '__main__':
    # config = utils.load_config()
    # path_to_tickers_data = config["data_directory"]["ticker_list"]
    # path_to_ticker_ignore = config["data_directory"]["ticker_ignore"]

    # st_config = config["stocktwits"]

    # trending_tickers = get_trending_tickers()

    stocktwits_bot = StocktwitsBot()
    stocktwits_bot.save_trending_tickers()


    
