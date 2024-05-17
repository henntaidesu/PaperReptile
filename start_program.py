import subprocess
import time
import requests

from src.module.read_conf import ReadConf


exe_path = r'./main.exe'

processes, state_interval = ReadConf().processes()


try:
    for _ in range(processes):
        subprocess.Popen(exe_path)
        time.sleep(state_interval)

except FileNotFoundError:
    print("文件未找到，请检查路径是否正确。")
except Exception as e:
    print("启动程序时出现错误:", e)
