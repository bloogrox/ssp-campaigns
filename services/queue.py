import json
import pika
from nameko.rpc import rpc
from app import rmq_pool


class Queue:
    name = "queue"

    @rpc
    def publish(self, payload):
        with rmq_pool.acquire() as cxn:
            try:
                cxn.channel.basic_publish(
                    body=json.dumps(payload),
                    exchange='',
                    routing_key='sell-imp',
                    properties=pika.BasicProperties(
                        content_type='plain/text'
                    )
                )
                subscriber_id = payload['subscriber']['_id']
                print(f"Queue.publish published: {subscriber_id}")
            except Exception as e:
                print(f"Queue.publish exception: {e}")
