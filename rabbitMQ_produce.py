import time
import pika
import threading
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


def CNKI_paper_title_status_0():
    queue_name = "paper_title_status=0"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT * FROM `Paper`.`cnki_index` WHERE receive_time > '2023-01-01' and db_type in ('1') and `status` = '0' limit 200"
            flag, data = Date_base().select(sql)
            if data:
                for i in data:
                    UUID = i[0]
                    title = i[1]
                    receive_time = str(i[2])
                    status = i[3]
                    db_type = i[4]
                    sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'Z' where `uuid` = '{UUID}';"
                    flag = Date_base().update(sql)
                    try:
                        title_producer(queue_name, f"{UUID},{title},{receive_time},{status},{db_type}")
                        Log().write_log(f"{queue_name} - {title} - {receive_time}", 'info')
                    except Exception as e:
                        Log().write_log(f"{queue_name} - {title}", 'error')
                        err2(e)
        else:
            time.sleep(60)
            continue


def CNKI_paper_title_status_a():
    queue_name = "paper_title_status=a"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT * FROM `Paper`.`cnki_index` WHERE db_type in ('1', '2', '3') and `status` = 'a' limit 20"
            flag, data = Date_base().select(sql)
            if data:
                for i in data:
                    UUID = i[0]
                    title = i[1]
                    receive_time = str(i[2])
                    status = i[3]
                    db_type = i[4]
                    sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'X' where `uuid` = '{UUID}';"
                    flag = Date_base().update(sql)
                    try:
                        title_producer(queue_name, f"{UUID},{title},{receive_time},{status},{db_type}")
                        Log().write_log(f"{queue_name} - {title}", 'info')
                    except Exception as e:
                        Log().write_log(f"{queue_name} - {title}", 'error')
                        err2(e)
        else:
            time.sleep(60)


def CNKI_paper_title_status_b():
    queue_name = "paper_title_status=b"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT * FROM `Paper`.`cnki_index` WHERE db_type in ('1', '2', '3') and `status` = 'b' limit 20"
            flag, data = Date_base().select(sql)
            if data:
                for i in data:
                    UUID = i[0]
                    title = i[1]
                    receive_time = str(i[2])
                    status = i[3]
                    db_type = i[4]
                    sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'Y' where `uuid` = '{UUID}';"
                    Date_base().update(sql)
                    try:
                        title_producer(queue_name, f"{UUID},{title},{receive_time},{status},{db_type}")
                        Log().write_log(f"{queue_name} - {title}", 'info')
                    except Exception as e:
                        Log().write_log(f"{queue_name} - {title}", 'error')
                        err2(e)
        else:
            time.sleep(60)


def ARXIV_paper_status_00():
    queue_name = "ARXIV_paper_status_00"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT UUID, classification_en FROM `index` WHERE  `from` = 'arxiv' and state = '00' limit 2000"
            flag, data = Date_base().select(sql)
            if data:
                for i in data:
                    uuid = i[0]
                    classification_en = i[1]
                    sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'AA' where `uuid` = '{uuid}';"
                    Date_base().update(sql)
                    try:
                        title_producer(queue_name, f"{uuid},{classification_en}")
                        Log().write_log(f"{queue_name} - {classification_en}", 'info')
                    except Exception as e:
                        Log().write_log(f"{queue_name} - {classification_en}", 'error')
                        err2(e)
        else:
            time.sleep(60)


def ARXIV_paper_status_01():
    queue_name = "ARXIV_paper_status_01"
    while True:
        if get_queue_quantity(queue_name) < ReadConf().rabbitMQ_max_queue():
            sql = f"SELECT UUID, title_en FROM `Paper`.`index` WHERE `from` = 'arxiv' and state = '01' limit 2000"
            flag, data = Date_base().select(sql)
            if data:
                for i in data:
                    UUID = i[0]
                    title_en = i[1]
                    sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'AB' where `uuid` = '{UUID}';"
                    Date_base().update(sql)
                    try:
                        title_producer(queue_name, f"{UUID},{title_en}")
                        Log().write_log(f"{queue_name} - {title_en}", 'info')
                    except Exception as e:
                        Log().write_log(f"{queue_name} - {title_en}", 'error')
                        err2(e)
        else:
            time.sleep(60)


if __name__ == '__main__':
    print("生产者已启动")
    thread1 = threading.Thread(target=CNKI_paper_title_status_0)
    thread2 = threading.Thread(target=CNKI_paper_title_status_a)
    thread3 = threading.Thread(target=CNKI_paper_title_status_b)
    thread4 = threading.Thread(target=ARXIV_paper_status_00)
    thread5 = threading.Thread(target=ARXIV_paper_status_01)
    # 启动线程
    try:
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
    except KeyboardInterrupt:
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()