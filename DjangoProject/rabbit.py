import pika
from pika.exchange_type import ExchangeType
from service_A import models
from DjangoProject import constants
import json


def enqueue_task(task: models.Task, code: int = constants.IN_PROGRESS_QUEUE_CODE):
    with pika.BlockingConnection(pika.ConnectionParameters()) as connection:
        with connection.channel() as channel:
            queue_name = constants.get_queue(code, task)

            channel.queue_declare(
                queue=queue_name,
                durable=True
            )
            channel.queue_declare(
                queue=constants.get_queue(code),
                durable=True
            )

            channel.exchange_declare(
                exchange=constants.QUEUE_NAMES[code],
                exchange_type=ExchangeType.topic,
            )

            channel.queue_bind(
                exchange=constants.QUEUE_NAMES[code],
                queue=constants.get_queue(code),
            )
            channel.queue_bind(
                exchange=constants.QUEUE_NAMES[code],
                queue=queue_name,
            )

            channel.basic_publish(
                exchange=constants.QUEUE_NAMES[code],
                routing_key=queue_name,
                body=json.dumps(
                    {
                        constants.TASK_CODE_TAG: task.id,
                        'code': constants.IN_PROGRESS_QUEUE_CODE,
                        'parameters': task.parameters,
                        'timeoutInSeconds': task.procedure_time
                    }
                ),
            )


def dequeue_task(task: models.Task, queue_code: int, func: callable, *, dequeue: bool = True):
    with pika.BlockingConnection(pika.ConnectionParameters()) as connection:
        with connection.channel() as channel:
            queue_name = constants.get_queue(queue_code, task)

            channel.queue_declare(
                queue=queue_name,
                durable=True
            )

            method, properties, body = func(
                channel.basic_get(
                    queue=queue_name,
                )
            )

            if not method or not properties:
                return

            if dequeue:
                channel.basic_ack(method.delivery_tag)

            return json.loads(body)


def clear_task(task: models.Task):
    with pika.BlockingConnection(pika.ConnectionParameters()) as connection:
        with connection.channel() as channel:
            channel.queue_delete(
                queue=constants.get_queue(task),
            )

def setup_consumer(queue_code: int, callback: callable):
    with pika.BlockingConnection(pika.ConnectionParameters()) as connection:
        with connection.channel() as channel:
            queue_name = constants.get_queue(queue_code)

            channel.exchange_declare(
                exchange=constants.QUEUE_NAMES[queue_code],
                exchange_type=ExchangeType.topic,
            )

            channel.queue_declare(
                queue=queue_name,
                durable=True
            )
            channel.queue_bind(
                exchange=constants.QUEUE_NAMES[queue_code],
                queue=queue_name,
            )

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
            )

            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                channel.stop_consuming()
                return
            except Exception as e:
                raise e

