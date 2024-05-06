import multiprocessing
from src.index import Index

# -*- coding: utf-8 -*-

if __name__ == '__main__':
    # 多进程
    multiprocessing.freeze_support()
    while True:
        Index().index()

