from nameko.testing.services import worker_factory

from services.campaigns_runner import CampaignsRunnerService
from services.counter import CounterService


def test_campaigns_runner_service():
    # create worker with mock dependencies
    service = worker_factory(CampaignsRunnerService)

    service.campaign_service.get_campaigns.return_value = [{"id": 1}]

    service.run()

    # service.campaign_service.get_campaigns.assert_called_once()
    # (service
    #  .campaign_processor_service
    #  .process_campaign
    #  .call_async
    #  .assert_called_once_with({"id": 1}))


def test_counter_service():
    service = worker_factory(CounterService)
    assert 0 == service.get_pushes_count("token")


# @todo #3:60min write tests for other services
