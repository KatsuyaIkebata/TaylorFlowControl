from logging import (getLogger, StreamHandler, INFO, Formatter)

# ログの設定
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(Formatter("[%(asctime)s] [%(threadName)s] %(message)s"))
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)


from threading import (Event, Thread)
import time
event = Event()

# イベント停止のフラグ
stop = False


def event_example3():
    logger.info("スレッド開始")
    count = 0
    print(f"bool of stop is {stop}")
    while not stop:
        event.wait()
        event.clear()
        count += 1
        logger.info(count)
    logger.info("スレッド終了")

thread = Thread(target=event_example3)
thread.start()

time.sleep(1)
event.set()
time.sleep(1)
event.set()
time.sleep(1)
stop = True
event.set()

thread.join()
