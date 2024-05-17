import pika
from src.module.execution_db import Date_base
from src.module.read_conf import ReadConf
from src.module.log import Log, err2
import threading

logger = Log()


def mysql_updata():
    while True:
        queue_name = "MYSQL_UPDATE"
        conf = ReadConf().rabbitMQ()
        connection_params = pika.ConnectionParameters(
            host=conf['host'],
            port=conf['port'],
            credentials=pika.PlainCredentials(username=conf['username'], password=conf['password'])
        )
        connection = None
        try:
            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()

            # 声明队列
            channel.queue_declare(queue=queue_name)
            while True:
                method_frame, header_frame, body = channel.basic_get(queue=queue_name)
                if method_frame:
                    message = body.decode()  # 处理消息
                    Date_base().update(message)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except KeyboardInterrupt:
            logger.write_log("程序关闭", 'ERROR')
            connection.close()


def mysql_insert():
    while True:
        queue_name = "MYSQL_INSERT"
        conf = ReadConf().rabbitMQ()
        connection_params = pika.ConnectionParameters(
            host=conf['host'],
            port=conf['port'],
            credentials=pika.PlainCredentials(username=conf['username'], password=conf['password'])
        )
        connection = None
        try:
            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()

            # 声明队列
            channel.queue_declare(queue=queue_name)
            while True:
                method_frame, header_frame, body = channel.basic_get(queue=queue_name)
                if method_frame:
                    message = body.decode()  # 处理消息
                    Date_base().update(message)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except KeyboardInterrupt:
            logger.write_log("程序关闭", 'ERROR')
            connection.close()


if __name__ == '__main__':
    print("数据库消费者已启动")
    thread1 = threading.Thread(target=mysql_updata)
    thread2 = threading.Thread(target=mysql_insert)

    try:
        thread1.start()
        thread2.start()
    except KeyboardInterrupt:
        thread1.join()
        thread2.join()
        logger.write_log("程序关闭", 'ERROR')
