from enum import Enum


class Product(Enum):
    all = "0"
    cash = "1"
    margin = "2"
    future = "3"
    option = "4"


class State(Enum):
    standby = "1"
    processing = "2"
    processed = "3"
    correcting = "4"
    finished = "5"


class Exchange(Enum):
    tosyou = 1
    meisyou = 3
    fukusyou = 5
    sassyou = 6


class Side(Enum):
    sell = "1"
    buy = "2"


class CashMargin(Enum):
    cash = 1
    margin = 2
    repay = 3


class MarginType(Enum):
    system = 1
    general = 2
    day_trade = 3


class DelivType(Enum):
    none = 0
    transfer = 1
    deposit = 2


class FundType(Enum):
    cash = "  "
    protect = "02"
    substitute_securities = "AA"
    margin_trade = "11"


class AccountType(Enum):
    normal = 2
    specific = 4
    corporation = 11


class ClosePosition(Enum):
    old_date_high_profit = 0
    old_date_low_profit = 1
    new_date_high_profit = 2
    new_date_low_profit = 3
    high_profit_old_date = 4
    high_profit_new_date = 5
    low_profit_old_date = 6
    low_profit_new_date = 7


class FrontOrderType(Enum):
    market = 10
    open_market_am = 13
    open_market_pm = 14
    close_market_am = 15
    close_market_pm = 16
    ioc_market = 17
    limit = 20
    open_limit_am = 21
    open_limit_pm = 22
    close_limit_am = 23
    close_limit_pm = 24
    no_limit_am = 25
    no_limit_pm = 26
    ioc_limit = 27
    reverse_limt = 30
