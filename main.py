import time

from station import Station


class MyStation(Station):
    def __init__(self, password, codes, retoken=True, test=False):
        super().__init__(password, retoken=retoken, test=test)
        self.codes = codes
        station.unregister_all()
        for code in codes:
            self.register_tosyou(code)

    def main(self):
        self.ws_runner()
        while True:
            self.lock.acquire()
            print(self.msgs)
            self.lock.release()
            time.sleep(0.5)


def main():
    with open("password.txt", "r") as f:
        password = f.read().strip()
    codes = (9202,)
    station = MyStation(password, codes)
    station.main()


if __name__ == "__main__":
    main()
