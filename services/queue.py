import json
import pika
from nameko.rpc import rpc
from app import rmq_pool


QUEUE = 'sell-imp'


class Queue:
    name = "queue"

    @rpc
    def publish(self, payload):
        with rmq_pool.acquire() as cxn:
            try:
                cxn.channel.queue_declare(queue=QUEUE, auto_delete=True)
                cxn.channel.queue_bind(queue=QUEUE,
                                       exchange='',
                                       routing_key=QUEUE)
                cxn.channel.basic_publish(
                    body=json.dumps(payload),
                    exchange='',
                    routing_key=QUEUE,
                    properties=pika.BasicProperties(
                        content_type='plain/text'
                    )
                )
                subscriber_id = payload['subscriber']['_id']
                print(f"Queue.publish published: {subscriber_id}")
            except Exception as e:
                print(f"Queue.publish exception: {e}")
