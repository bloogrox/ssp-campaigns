from datetime import datetime
import pytz

from nameko.rpc import rpc
from elasticsearch_dsl import Search, Q, query as dslq
from app import es


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, targetings, hours_whitelist, volume):
        print("SubscriberService.get_subscribers: getting subscribers")
        timezones = [tz for tz in pytz.all_timezones
                     if (datetime
                         .now(pytz.timezone(tz)).hour
                         in hours_whitelist)]

        targetings.append({
            "field": "unsub",
            "operator": "NOT IN",
            "values": [1, "true"]
        })
        if timezones:
            targetings.append({
                "field": "timezone",
                "operator": "IN",
                "values": timezones
            })
        try:
            s = Search(using=es, index="users")
            operator_mappings = {
                'IN': 'must',
                'NOT IN': 'must_not',
            }

            q = Q()
            for condition in targetings:
                condition_pair = {condition["field"]: condition["values"]}
                terms_q = Q('terms', **condition_pair)
                bool_operator = operator_mappings[condition['operator']]
                bool_q = Q('bool', **{bool_operator: terms_q})
                q += bool_q
            s = s.query(q)
            s.query = dslq.FunctionScore(
                query=s.query,
                functions=[dslq.SF('random_score')],
                boost_mode="replace"
                )
            s = s[:volume]
            res = s.execute()
            subscribers = []
            for row in res.hits:
                subscriber = row.to_dict()
                subscriber['_id'] = row.meta.id
                subscribers.append(subscriber)
            return subscribers
        except Exception as e:
            print(f"SubscriberService.get_subscribers: Exception {e}")

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
