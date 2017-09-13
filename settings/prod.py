import os


REDIS_URI = os.environ["REDIS_URL"]
AMQP_URI = os.environ["RABBITMQ_URL"]
PUSHW_AUTH_TOKEN = os.environ["PUSHW_AUTH_TOKEN"]
PUSHW_AUTH_KEY = os.environ["PUSHW_AUTH_KEY"]
ELASTIC_URI = os.environ['ELASTICSEARCH_URI']
LIMIT_PER_USER = 3
CABINET_URL = os.environ['CABINET_URL']
LOG_LEVEL = os.environ.get('LOG_LEVEL') or "INFO"
