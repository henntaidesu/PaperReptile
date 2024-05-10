import pika
from src.module.read_conf import ReadConf
from src.module.log import Log


def rabbitmq_consume(queue_name):
    conf = ReadConf().rabbitMQ()
    connection_params = pika.ConnectionParameters(
        host=conf['host'],
        port=conf['port'],
        credentials=pika.PlainCredentials(username=conf['username'], password=conf['password'])
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=False)  # 声明队列，持久性参数与当前队列保持一致
    method_frame, header_frame, body = channel.basic_get(queue=queue_name)
    if method_frame:
        message = body.decode()  # 处理消息
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)  # 标记消息为已消费
        connection.close()
        return message
    else:
        Log().write_log(f"队列 - {queue_name} 为空", "error")
        connection.close()
        return None


def rabbitmq_produce(queue_name, message):
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
