campaigns_runner_service: nameko run --config nameko.configs/campaigns.yml services.campaigns_runner:CampaignsRunnerService
campaign_service: nameko run --config nameko.configs/campaigns.yml services.campaign:CampaignService
stats_service: nameko run --config nameko.configs/campaigns.yml services.stats:StatsService
subscriber_service: nameko run --config nameko.configs/campaigns.yml services.subscriber:SubscriberService
campaign_processor_service: nameko run --config nameko.configs/campaigns.yml services.campaign_processor:CampaignProcessorService
queue: nameko run --config nameko.configs/campaigns.yml services.queue:Queue
counter_service: nameko run --config nameko.configs/campaigns.yml services.counter:CounterService
subscriber_processor_service: nameko run --config nameko.configs/campaigns.yml services.subscriber_processor:SubscriberProcessorService
timer: nameko run --config nameko.configs/timer.yml services.timer:Timer
start_syncer: bin/start_syncer.sh
