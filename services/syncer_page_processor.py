from nameko.rpc import rpc, RpcProxy


class SyncerPageProcessorService:
    name = "syncer_page_processor_service"

    syncer_subscriber_augmentor_service = (
        RpcProxy("syncer_subscriber_augmentor_service"))
    subscriber_remote_storage_service = (
        RpcProxy("subscriber_remote_storage_service"))

    @rpc
    def process_page(self, limit, page_number):
        subscribers = (self.subscriber_remote_storage_service
                       .subscribers(limit, page_number))
        print("SyncerService.process_page: "
              f"page {page_number} loaded")
        for subscriber in subscribers:
            (self.syncer_subscriber_augmentor_service.augment
             .call_async(subscriber))
