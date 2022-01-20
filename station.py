from pprint import pprint
import json
from datetime import datetime
import pickle

import requests
import asyncio
import websockets

from enums import (
    Product,
    State,
    Exchange,
    Side,
    CashMargin,
    MarginType,
    DelivType,
    FundType,
    AccountType,
    ClosePosition,
    FrontOrderType,
)


class Station(object):
    def __init__(self, password, test=False, retoken=True):
        self.running = True
        self.password = password
        if test:
            port = 18081
        else:
            port = 18080
        self.rest_url = f"http://localhost:{port}/kabusapi"
        self.ws_url = f"ws://localhost:{port}/kabusapi/websocket"

        if retoken:
            r = requests.request(
                "POST", self.rest_url + "/token", json={"APIPassword": password}
            )
            self.token = Station.parse(r)["Token"]
            with open("./cache/token.pkl", "wb") as f:
                pickle.dump(self.token, f)
        else:
            with open("./cache/token.pkl", "rb") as f:
                self.token = pickle.load(f)

    def get_all_orders(self):
        return self.rest("GET", "/orders")

    def get_wallet_margin(self):
        return self.rest("GET", "/wallet/margin")

    def get_margin_positions(self):
        positions = self.get_positions(product=Product.margin)
        rsts = list()
        for position in positions:
            if position["HoldQty"] != 0 or position["LeavesQty"] != 0:
                rsts.append(position)
        return rsts

    def get_margin_orders(self):
        orders = self.get_orders(product=Product.margin)
        rsts = list()
        for order in orders:
            if order["State"] != 5:
                rsts.append(order)
        return rsts

    def get_positions(
        self,
        product=None,
        symbol=None,
        side=None,
        addinfo=None,
    ):
        params = dict()
        if product is not None:
            params["product"] = product.value
        if symbol is not None:
            params["symbol"] = symbol
        if side is not None:
            params["side"] = side.value
        if addinfo is not None:
            params["addinfo"] = addinfo
        return self.rest("GET", "/positions", params=params)

    def get_orders(
        self,
        product=None,
        id=None,
        updtime=None,
        details=None,
        symbol=None,
        state=None,
        side=None,
        cashmargin=None,
    ):
        params = dict()
        if product is not None:
            params["product"] = product.value
        if id is not None:
            params["id"] = id
        if updtime is not None:
            params["updtime"] = updtime
        if details is not None:
            params["details"] = details
        if symbol is not None:
            params["symbol"] = symbol
        if state is not None:
            params["state"] = state.value
        if side is not None:
            params["side"] = side.value
        if cashmargin is not None:
            params["cashmargin"] = cashmargin.value
        return self.rest("GET", "/orders", params=params)

    def send_order(
        self,
        symbol,
        exchange: Exchange,
        side: Side,
        cash_margin: CashMargin,
        deliv_type: DelivType,
        account_type: AccountType,
        qty,
        front_order_type: FrontOrderType,
        price=0,
        expire_day=0,
        fund_type=None,
        margin_trade_type=None,
        close_position_order=None,
        close_positions=None,
        reserve_limit_order=None,
    ):
        json = {
            "Password": self.password,
            "Symbol": symbol,
            "Exchange": exchange.value,
            "SecurityType": 1,
            "Side": side.value,
            "CashMargin": cash_margin.value,
            "DelivType": deliv_type.value,
            "AccountType": account_type.value,
            "Qty": qty,
            "FrontOrderType": front_order_type.value,
            "Price": price,
            "ExpireDay": expire_day,
        }
        if fund_type:
            json["FundType"] = fund_type.value
        if margin_trade_type:
            json["MarginTradeType"] = margin_trade_type.value
        if close_position_order:
            json["ClosePositionOrder"] = close_position_order.value
        if close_positions:
            json["ClosePositions"] = close_positions
        if reserve_limit_order:
            json["ReverseLimitOrder"] = reserve_limit_order
        return self.rest("POST", "/sendorder", json)

    def margin_sell_limit(self, symbol, price, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.sell,
            CashMargin.margin,
            DelivType.none,
            AccountType.normal,
            qty,
            FrontOrderType.limit,
            price=price,
            margin_trade_type=MarginType.system,
        )

    def margin_sell_market(self, symbol, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.sell,
            CashMargin.margin,
            DelivType.none,
            AccountType.normal,
            qty,
            FrontOrderType.market,
            margin_trade_type=MarginType.system,
        )

    def margin_buy_limit(self, symbol, price, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.buy,
            CashMargin.margin,
            DelivType.none,
            AccountType.normal,
            qty,
            FrontOrderType.limit,
            price=price,
            margin_trade_type=MarginType.system,
        )

    def margin_buy_market(self, symbol, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.buy,
            CashMargin.margin,
            DelivType.none,
            AccountType.normal,
            qty,
            FrontOrderType.market,
            margin_trade_type=MarginType.system,
        )

    def repay_buy_market(self, symbol, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.buy,
            CashMargin.repay,
            DelivType.deposit,
            AccountType.normal,
            qty,
            FrontOrderType.market,
            margin_trade_type=MarginType.system,
            close_position_order=ClosePosition.high_profit_old_date,
        )

    def repay_sell_market(self, symbol, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.sell,
            CashMargin.repay,
            DelivType.deposit,
            AccountType.normal,
            qty,
            FrontOrderType.market,
            margin_trade_type=MarginType.system,
            close_position_order=ClosePosition.high_profit_old_date,
        )

    def repay_buy_limit(self, symbol, price, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.buy,
            CashMargin.repay,
            DelivType.deposit,
            AccountType.normal,
            qty,
            FrontOrderType.limit,
            price=price,
            margin_trade_type=MarginType.system,
            close_position_order=ClosePosition.high_profit_old_date,
        )

    def repay_sell_limit(self, symbol, price, qty):
        return self.send_order(
            symbol,
            Exchange.tosyou,
            Side.sell,
            CashMargin.repay,
            DelivType.deposit,
            AccountType.normal,
            qty,
            FrontOrderType.limit,
            price=price,
            margin_trade_type=MarginType.system,
            close_position_order=ClosePosition.high_profit_old_date,
        )

    def cancel_order(self, order_id):
        json = {
            "OrderId": order_id,
            "Password": self.password,
        }
        return self.rest("PUT", "/cancelorder", json)

    def register(self, symbols):
        json = {"Symbols": symbols}
        return self.rest("PUT", "/register", json)

    def unregister(self, symbols):
        json = {"Symbols": symbols}
        return self.rest("PUT", "/unregister", json)

    def unregister_all(self):
        return self.rest("PUT", "/unregister/all")

    def register_tosyou(self, symbol):
        self.register([{"Symbol": str(symbol), "Exchange": Exchange.tosyou.value}])

    def rest(self, method, api, json=None, params=None):
        headers = {"X-API-KEY": self.token}
        r = requests.request(
            method, self.rest_url + api, json=json, params=params, headers=headers
        )
        return Station.parse(r)

    def msg_handler(self, msg):
        print(msg)
        print("Inherit Station class and rewrite this (msg_handler) method...")

    @staticmethod
    def parse(r):
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            pprint(json.loads(r.content))
            raise requests.HTTPError(f"\n\n{r.status_code}: {r.reason}\n")

    def run(self):
        async def main():
            async with websockets.connect(
                self.ws_url, ping_interval=None, close_timeout=0
            ) as ws:
                while self.running:
                    msg = await ws.recv()
                    self.msg_handler(msg)

        asyncio.run(main())
