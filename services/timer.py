from nameko.rpc import RpcProxy
from nameko.timer import timer
from app import logger


class Timer:
    name = "timer_service"

    campaigns_runner_service = RpcProxy("campaigns_runner_service")
    syncer_service = RpcProxy("syncer_service")

    @timer(interval=1)
    def run_campaigns(self):
        logger.debug("tick")
        self.campaigns_runner_service.run.call_async()
