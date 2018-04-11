import time
import pykka
import json
import pika
from uuid import uuid4
from app import rmq_pool, logger


QUEUE_NAME = 'bid-request'


class SspPy(pykka.ThreadingActor):
    def on_receive(self, payload):
        s = payload["subscriber"]
        s["ext_data"] = {}
        for f in payload["campaign"]["dsp"]["ext_fields"]:
            if f in s:
                if s[f] is not None:
                    s["ext_data"][f] = str(s[f])

        data = {
            "dsp": payload["campaign"]["dsp"],
            "subscriber": s
        }

        message = {
            "queue_name": QUEUE_NAME,
            "actor_name": "send_bid_request",
            "args": [data],
            "kwargs": {},
            "options": {},
            "message_id": str(uuid4()),
            "message_timestamp": round(time.time() * 1000),
        }

        with rmq_pool.acquire() as cxn:
            try:
                cxn.channel.queue_declare(queue=QUEUE_NAME, auto_delete=True)
                cxn.channel.basic_publish(
                    body=json.dumps(message),
                    exchange='',
                    routing_key=QUEUE_NAME,
                    properties=pika.BasicProperties(
                        content_type='plain/text'
                    )
                )
                subscriber_id = payload['subscriber']['_id']
                logger.debug(f"Queue.publish published: {subscriber_id}")
            except Exception as e:
                logger.error(f"Queue.publish exception: {e}")
