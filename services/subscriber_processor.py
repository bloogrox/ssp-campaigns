from nameko.rpc import rpc, RpcProxy
from cabinet import Cabinet


class SubscriberProcessorService:
    name = "subscriber_processor_service"

    counter_service = RpcProxy("counter_service")
    queue = RpcProxy("queue")

    @rpc
    def process_subscriber(self, payload):
        print("SubscriberProcessorService.process_subscriber: "
              f"processing subscriber: {payload}")
        cab = Cabinet("https://ssp-cabinet.herokuapp.com")
        general_settings = cab.general()
        limit = general_settings["push_limit_per_token"]
        if self.counter_service.get_pushes_count(payload["_id"]) <= limit:
            self.queue.publish.call_async(payload)
        else:
            print("SubscriberProcessorService.process_subscriber: "
                  f"limit for subscriber: {payload} exceeded")
