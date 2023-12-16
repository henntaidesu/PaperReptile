import multiprocessing
from src.index import index


if __name__ == '__main__':
    # 多进程
    multiprocessing.freeze_support()
    while True:
        Index = index()
        Index.index()

