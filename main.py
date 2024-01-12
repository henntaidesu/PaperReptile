import multiprocessing
from src.index import index
import time
from datetime import datetime

if __name__ == '__main__':
    # 多进程
    multiprocessing.freeze_support()
    while True:
        # current_time = datetime.now().time()
        #
        # if current_time >= datetime.strptime('23:00', '%H:%M').time() or \
        #         current_time < datetime.strptime('08:00', '%H:%M').time():
        #     print("程序休眠 23-8点休眠")
        #     time.sleep(25000)
        # else:
        #     time.sleep(300)
        Index = index()
        Index.index()

