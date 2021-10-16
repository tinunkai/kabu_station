from station import Station


class MyStation(Station):
    def msg_handler(self, msg):
        print(msg)


def main():
    station = MyStation("password")
    station.unregister_all()
    station.register_tosyou(7974)
    station.run()


if __name__ == "__main__":
    main()
