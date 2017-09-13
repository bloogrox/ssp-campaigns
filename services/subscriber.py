import time
from datetime import datetime
import pytz

from nameko.rpc import rpc
from elasticsearch_dsl import Search, Q, query as dslq
from app import es, logger


class SubscriberService:
    name = "subscriber_service"

    @rpc
    def get_subscribers(self, targetings, hours_whitelist, volume):
        logger.info("SubscriberService.get_subscribers: getting subscribers")
        start_time = time.time()
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
        try:
            res = s.execute()
        except Exception as e:
            logger.error(f"SubscriberService.get_subscribers: Exception {e}")
        else:
            subscribers = []
            for row in res.hits:
                subscriber = row.to_dict()
                subscriber['_id'] = row.meta.id
                subscribers.append(subscriber)
            end_time = time.time()
            logger.debug(f"SubscriberService.get_subscribers: finished in "
                         f"{int((end_time - start_time) * 1000)}ms")
            return subscribers
