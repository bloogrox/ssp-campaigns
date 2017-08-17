from nameko.testing.services import worker_factory

from services.queue import Queue


def test_campaigns_runner_service():
    service = worker_factory(Queue)
    service.publish({'subscriber': {'_id': 'cd6b4a665'}})
