import requests
import pandas as pd
from dateutil.parser import *
import main
import utils
import sys
import json

from oanda_trade import OandaTrade
from oanda_price import OandaPrice


class OandaAPI():

    def __init__(self):
        self.session = requests.Session()

    def make_request(self, url, params={}, added_headers=None, verb='get', data=None, code_ok=200):

        headers = main.SECURE_HEADER

        if added_headers is not None:
            for k in added_headers.keys():
                headers[k] = added_headers[k]

        try:
            response = None
            if verb == 'post':
                response = self.session.post(url, params=params, headers=headers, data=data)
            elif verb == 'put':
                response = self.session.put(url, params=params, headers=headers, data=data)
            else:
                response = self.session.get(url, params=params, headers=headers, data=data)

            status_code = response.status_code

            if status_code == code_ok:
                json_response = response.json()
                return status_code, json_response
            else:
                return status_code, None

        except:
            print("ERROR")
            return 400, None


    def close_trade(self, trade_id):
        url = f"{main.OANDA_URL}/accounts/{main.ACCOUNT_ID}/trades/{trade_id}/close"
        status_code, json_data = self.make_request(url, verb='put', code_ok=200)
        if status_code != 200:
            return False
        return True

    def set_sl_tp(self, price, order_type, trade_id):
        url = f"{main.OANDA_URL}/accounts/{main.ACCOUNT_ID}/orders"
        data = {
            "order": {
                "timeInForce": "GTC",
                "price": str(price),
                "type": order_type,
                "tradeID": str(trade_id)
            }
        }
        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)

        if status_code != 201:
            return False
        return True

    def place_trade(self, pair, units, take_profit=None, stop_loss=None):
        url = f"{main.OANDA_URL}/accounts/{main.ACCOUNT_ID}/orders"

        data = {
            "order": {
                "units": units,
                "instrument": pair,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        print(data)
        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)
        print(status_code, json_data)

        if status_code != 201:
            return None

        trade_id = None
        ok = True

        if "orderFillTransaction" in json_data and "tradeOpened" in json_data["orderFillTransaction"]:
            trade_id = int(json_data["orderFillTransaction"]["tradeOpened"]["tradeID"])
            if take_profit is not None:
                if (self.set_sl_tp(take_profit, "TAKE_PROFIT", trade_id) == False):
                    ok = False
            if stop_loss is not None:
                if (self.set_sl_tp(stop_loss, "STOP_LOSS", trade_id) == False):
                    ok = False

        return trade_id

    def open_trades(self):
        url = f"{main.OANDA_URL}/accounts/{main.ACCOUNT_ID}/openTrades"
        status_code, data = self.make_request(url)

        if status_code != 200:
            return [], False

        if 'trades' not in data:
            return [], True

        trades = [OandaTrade.TradeFromAPI(x) for x in data['trades']]

        return trades, True





if __name__ == "__main__":
    api = OandaAPI()

    code, prices = api.fetch_prices(['EUR_USD', 'SGD_CHF'])
    print(prices)