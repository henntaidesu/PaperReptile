import time
import pika
from src.module.execution_db import Date_base
from src.module.read_conf import ReadConf
from src.module.log import Log, err2


def title_producer(queue_name, message):
    # 建立 RabbitMQ 连接
    conf = ReadConf().rabbitMQ()
    connection_params = pika.ConnectionParameters(
        host=conf['host'],
        port=conf['port'],
        credentials=pika.PlainCredentials(username=conf['username'], password=conf['password'])
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # 声明队列
    channel.queue_declare(queue=queue_name)

    # 发送消息到指定队列，同时传入键
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)

    # 关闭连接
    connection.close()


def get_queue_quantity(queue_name):
    conf = ReadConf().rabbitMQ()
    connection_params = pika.ConnectionParameters(
        host=conf['host'],
        port=conf['port'],
        credentials=pika.PlainCredentials(username=conf['username'], password=conf['password'])
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, passive=True)
    queue_state = channel.queue_declare(queue=queue_name, passive=True)
    message_count = queue_state.method.message_count
    connection.close()

    return message_count


def paper_title_status0():
    queue_name = "paper_title_status=0"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT * FROM `Paper`.`cnki_index` WHERE db_type in ('1', '2', '3') and `status` = '0' limit 1"
            flag, data = Date_base().select(sql)
            data = data[0]
            UUID = data[0]
            title = data[1]
            receive_time = str(data[2])
            status = data[3]
            db_type = data[4]
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'Z' where `uuid` = '{UUID}';"
            Date_base().update(sql)
            try:
                title_producer(queue_name, f"{UUID},{title},{receive_time},{status},{db_type}")
                Log().write_log(f"{queue_name} - {title}", 'info')
            except Exception as e:
                Log().write_log(f"{queue_name} - {title}", 'error')
                err2(e)
        else:
            time.sleep(0.2)
            continue


def paper_title_status9():
    queue_name = "paper_title_status=9"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT * FROM `Paper`.`cnki_index` WHERE db_type in ('1', '2', '3') and `status` = '9' limit 1"
            flag, data = Date_base().select(sql)
            data = data[0]
            UUID = data[0]
            title = data[1]
            receive_time = str(data[2])
            status = data[3]
            db_type = data[4]
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'Z' where `uuid` = '{UUID}';"
            Date_base().update(sql)
            try:
                title_producer(queue_name, f"{UUID},{title},{receive_time},{status},{db_type}")
                Log().write_log(f"{queue_name} - {title}", 'info')
            except Exception as e:
                Log().write_log(f"{queue_name} - {title}", 'error')
                err2(e)
        else:
            time.sleep(1)


if __name__ == '__main__':
    print("生产者已启动")
    paper_title_status0()
    paper_title_status9()
