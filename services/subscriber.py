from datetime import datetime, timedelta
import pytz

from nameko.rpc import rpc
from app import es


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, countries, time_stamp, limit):
        print("SubscriberService.get_subscribers: getting subscribers")
        try:
            country_filter = []
            for country in countries:
                country_filter.append({
                    "match": {
                        "country": country
                    }
                })

            timezone_filter = []
            if time_stamp:
                timezones = [tz for tz in pytz.all_timezones 
                if (datetime.utcnow() + timedelta(
                    hours = (datetime.now(
                    pytz.timezone(tz)).utcoffset().total_seconds() / 3600)))
                    .strftime('%H') == time_stamp]
                for timezone in timezones:
                    timezone_filter.append({
                        "match_phrase": {
                            "timezone": timezone
                        }
                    })
            res = es.msearch(body=[{"index": "subscribers"},
                                   {"size": limit,
                                    "query": {
                                        "function_score": {
                                            "query": {
                                                "bool": {
                                                    "should": country_filter,
                                                    "filter": {
                                                        "bool": {
                                                            "should": timezone_filter
                                                        }
                                                    }
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
