from pprint import pprint
import json

import requests
import asyncio
import websockets

from enums import (
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
    def __init__(self, password, test=False):
        self.password = password
        if test:
            port = 18081
        else:
            port = 18080
        self.rest_url = f"http://localhost:{port}/kabusapi"
        self.ws_url = f"ws://localhost:{port}/kabusapi/websocket"

        r = requests.request(
            "POST", self.rest_url + "/token", json={"APIPassword": password}
        )
        self.token = Station.parse(r)["Token"]

    def msg_handler(self, msg):
        print(msg)
        print("Inherit Station class and rewrite this (msg_handler) method...")

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

    def rest(self, method, api, json=None):
        headers = {"X-API-KEY": self.token}
        r = requests.request(method, self.rest_url + api, json=json, headers=headers)
        return Station.parse(r)

    @staticmethod
    def parse(r):
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            pprint(json.loads(r.content))
            raise requests.HTTPError(f"\n\n{r.status_code}: {r.reason}\n")

    def run(self):
        async def main():
            async with websockets.connect(self.ws_url, ping_interval=None) as ws:
                while True:
                    msg = await ws.recv()
                    self.msg_handler(msg)

        asyncio.run(main())
