from nameko.rpc import rpc, RpcProxy
import settings


class SubscriberProcessorService:
    name = "subscriber_processor_service"

    counter_service = RpcProxy("counter_service")
    queue = RpcProxy("queue")

    @rpc
    def process_subscriber(self, payload):
        # @todo #11:30min filter user by timezone
        print("SubscriberProcessorService.process_subscriber: "
              f"processing subscriber: {payload}")
        if self.counter_service.get_pushes_count("token") \
                <= settings.LIMIT_PER_USER:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"limit for subscriber: {payload} exceeded")
