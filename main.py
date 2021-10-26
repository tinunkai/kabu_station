from pprint import pprint

import json
from datetime import datetime

from station import Station


class MyStation(Station):
    def msg_handler(self, msg):
        msg = json.loads(msg)
        now = datetime.now()
        print(now, msg["SymbolName"], msg["CurrentPrice"])


def main():
    with open("password.txt", "r") as f:
        password = f.read().strip()
    station = MyStation(password)
    station.unregister_all()
    station.register_tosyou(9202)
    station.run()


if __name__ == "__main__":
    main()
