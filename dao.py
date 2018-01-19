import time
from datetime import datetime
import pytz

from elasticsearch.exceptions import ElasticsearchException
from elasticsearch_dsl import Search, Q, query as dslq
from app import es, logger


def get_subscribers(targetings, hours_whitelist, volume):
    logger.info("get_subscribers: getting subscribers")
    start_time = time.time()
    timezones = [tz
                 for tz in pytz.all_timezones
                 if datetime.now(pytz.timezone(tz)).hour in hours_whitelist]

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
    es_search = Search(using=es, index="users")
    operator_mappings = {
        'IN': 'must',
        'NOT IN': 'must_not',
    }

    es_query = Q()
    for condition in targetings:
        condition_pair = {condition["field"]: condition["values"]}
        terms_q = Q('terms', **condition_pair)
        bool_operator = operator_mappings[condition['operator']]
        bool_q = Q('bool', **{bool_operator: terms_q})
        es_query += bool_q
    es_search = es_search.query(es_query)
    es_search.query = dslq.FunctionScore(
        query=es_search.query,
        functions=[dslq.SF('random_score')],
        boost_mode="replace"
        )
    es_search = es_search[:volume]
    try:
        res = es_search.execute()
    except ElasticsearchException as e:
        logger.error(f"get_subscribers: Exception {e}")
    else:
        subscribers = []
        for row in res.hits:
            subscriber = row.to_dict()
            subscriber['_id'] = row.meta.id
            subscribers.append(subscriber)
        end_time = time.time()
        logger.debug(f"get_subscribers: finished in "
                     f"{int((end_time - start_time) * 1000)}ms")
        return subscribers
