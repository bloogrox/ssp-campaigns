from nameko.rpc import rpc, RpcProxy


class SyncerService:
    name = "syncer_service"

    subscriber_remote_storage_service = (
        RpcProxy("subscriber_remote_storage_service"))
    syncer_page_processor_service = RpcProxy("syncer_page_processor_service")

    @rpc
    def run(self):
        total_count = self.subscriber_remote_storage_service.get_total_count()
        print(f"SyncerService.run: total count is {total_count}")
        for page_number in range((total_count // 1000) + 1):
            (self.syncer_page_processor_service.process_page
             .call_async(1000, page_number))
