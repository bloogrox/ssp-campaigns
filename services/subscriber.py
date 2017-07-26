from nameko.rpc import rpc
from app import es


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, country_blacklist, limit):
        print("SubscriberService.get_subscribers: getting subscribers")
        try:
            country_filter = []
            for country in country_blacklist:
                country_filter.append({
                    "match": {
                        "country": country
                    }
                })
            res = es.msearch(body=[{"index": "subscribers"},
                                   {"size": limit,
                                    "query": {
                                        "function_score": {
                                            "query": {
                                                "bool": {
                                                    "must_not": country_filter
                                                }
                                            },
                                            "functions": [
                                                {
                                                    "random_score": {}
                                                }
                                            ]

                                        }
                                    }
                                    }
                                   ])
            subscribers = []
            for row in res['responses'][0]['hits']['hits']:
                subscriber = row['_source']
                subscriber['_id'] = row['_id']
                subscribers.append(subscriber)
            return subscribers
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
