import pykka
import json
import pika
from app import rmq_pool, logger


QUEUE_NAME = 'sell-imp'


class Queue(pykka.ThreadingActor):
    def on_receive(self, payload):
        with rmq_pool.acquire() as cxn:
            try:
                cxn.channel.queue_declare(queue=QUEUE_NAME, auto_delete=True)
                cxn.channel.basic_publish(
                    body=json.dumps(payload),
                    exchange='',
                    routing_key=QUEUE_NAME,
                    properties=pika.BasicProperties(
                        content_type='plain/text'
                    )
                )
                subscriber_id = payload['subscriber']['_id']
                logger.info(f"Queue.publish published: {subscriber_id}")
            except Exception as e:
                logger.error(f"Queue.publish exception: {e}")
