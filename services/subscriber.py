from nameko.rpc import rpc
from app import mongo_database
from app import es


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, filters, limit):
        print("SubscriberService.get_subscribers: getting subscribers")
        pipeline = [
            # {"country_code": {"$not": {"$in": ["USA"]}}}
            # {"$project": {
            #     "_id": 0,
            #     "uid": 1
            # }},
            {"$match": filters},
            {"$sample": {"size": limit}}
        ]
        try:
            return list(mongo_database.subscribers.aggregate(pipeline))
        except Exception as e:
            print("SubscriberService.get_subscribers: Exception " + str(e))

    @rpc
    def update_subscriber(self, document):
        try:
            sid = document['_id']
            document.pop('_id', None)
            es.index(index="subscribers", doc_type="post",
                     id=sid, body=document)
            print("SubscriberService.update_subscriber: "
                  f"persisting done successfully for {sid}")
        except Exception as e:
            print("SubscriberService.update_subscriber: "
                  "Exception " + str(e))
