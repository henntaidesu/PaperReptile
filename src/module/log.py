import logging
from src.module.now_time import day
from src.module.read_conf import read_conf


class log:
    def __init__(self):
        self.day = day()
        self.logger = self.setup_logger()
        self.confing = read_conf()
        self.log_level = self.confing.log_level()

    def setup_logger(self):
        log_file = f"log/{self.day}.log"
        # 创建一个logger对象
        logger = logging.getLogger("my_logger")
        logger.setLevel(logging.DEBUG)

        # 清除现有的处理器，以防止累积
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 创建一个文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # 创建一个控制台处理器，将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 定义日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到logger对象
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def write_log(self, text):
        # 输出不同级别的日志
        if self.log_level == "debug":
            self.logger.debug(text)
        elif self.log_level == "info":
            self.logger.info(text)
        elif self.log_level == "warning":
            self.logger.warning(text)
        elif self.log_level == "error":
            self.logger.error(text)
        elif self.log_level == "critical":
            self.logger.critical(text)

        # 检查是否开始了新的一天，如果是，则更新日志文件名
        new_day = day()
        if new_day != self.day:
            self.day = new_day
            # 在创建新处理器之前关闭旧的文件处理器
            self.logger.handlers[0].close()
            self.logger = self.setup_logger()
