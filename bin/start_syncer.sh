#!/bin/sh

nameko run --config nameko.configs/syncer.yml \
    services.syncer:SyncerService \
    services.syncer_subscriber_augmentor:SyncerSubscriberAugmentorService \
    services.syncer_page_processor:SyncerPageProcessorService \
    services.subscriber_remote_storage:SubscriberRemoteStorageService
