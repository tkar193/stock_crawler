import base64
import json
import sys
import os

from decouple import config
import finnhub
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..")

from common import utils

finnhub_client = None



class FinhubClient():
    def __init__(self):
        finnhub_config = base64.b64decode(config("FINNHUB_SECRETS"))
        finnhub_config = json.loads(finnhub_config)["finnhub_secrets"]
        finnhub_api_key = finnhub_config["api_key"]
        self.finnhub_client = finnhub.Client(api_key = finnhub_api_key)
        self.technical_status = None

    def get_technical_indicator(self, symbol, from_date, to_date, indicator = "stoch", resolution = 1):
        data = self.finnhub_client.technical_indicator(symbol = symbol, resolution = resolution, indicator = indicator, _from = from_date, to = to_date)
        slowd = data["slowd"]
        slowk = data["slowk"]
        vals = []

        # print(slowd)
        # return slowd[-1]

        for i in range(len(slowk)):
            val = (slowk[i] + slowd[i]) / 2
            val = utils.truncate(val, 0)
            vals.append(val)
            
            if val == 0:
                continue
            if val < 20:
                print(str(i) + ": " + str(val))
                print("---- OVERSOLD")
                if self.technical_status is None:
                    self.technical_status = "OVERSOLD"
            elif val > 80:
                print(str(i) + ": " + str(val))
                print("---- OVERBOUGHT")
                if self.technical_status is None:
                    self.technical_status = "OVERBOUGHT"

        plt.plot(slowd)
        # plt.plot(slowk)
        plt.xticks(np.arange(0, 420, 60))
        plt.show()






if __name__ == '__main__':
    
    symbol = "QQQ"
    finnhub_client = FinhubClient()
    
    

    from_date = utils.get_time_unix_from_date("2022-01-20T09:00")
    to_date = utils.get_time_unix_from_date("2022-01-20T16:00")

    finnhub_client.get_technical_indicator(symbol, from_date, to_date)





