import multiprocessing
from src.index import Index

if __name__ == '__main__':
    # 多进程
    multiprocessing.freeze_support()
    while True:
        Index().index()

