import os


def create_folder(path):
    # 使用os.makedirs()创建文件夹，如果文件夹已存在则不会引发错误
    os.makedirs(path, exist_ok=True)


