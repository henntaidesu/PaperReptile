import multiprocessing
from src.index import Index
from src.module.log import Log
import ctypes


if __name__ == '__main__':
    # 多进程
    multiprocessing.freeze_support()
    try:
        while True:
            Index().index()
    except KeyboardInterrupt:
        Log().write_log("程序关闭", 'ERROR')



