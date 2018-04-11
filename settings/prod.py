import os


REDIS_URI = os.environ["REDIS_URL"]
AMQP_URI = os.environ["RABBITMQ_URL"]
PUSHW_AUTH_TOKEN = os.environ["PUSHW_AUTH_TOKEN"]
PUSHW_AUTH_KEY = os.environ["PUSHW_AUTH_KEY"]
ELASTIC_URI = os.environ['ELASTICSEARCH_URI']
LIMIT_PER_USER = 3
CABINET_URL = os.environ['CABINET_URL']
LOG_LEVEL = os.environ.get('LOG_LEVEL') or "INFO"

SSP_URL = os.environ['SSP_URL']
SSP_VERSION = int(os.environ['SSP_VERSION'])
SSP_VERSIONS = [1, 2, 3]
if SSP_VERSION not in SSP_VERSIONS:
    raise Exception(f"SSP_VERSION must be one of {SSP_VERSIONS}")
if SSP_VERSION == 2 and not len(SSP_URL):
    raise Exception("SSP_URL is required when SSP_VERSION=2")
