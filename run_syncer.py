from nameko.cli.shell import make_nameko_helper
from nameko.constants import AMQP_URI_CONFIG_KEY
import os

config = {AMQP_URI_CONFIG_KEY: os.environ["RABBITMQ_BIGWIG_URL"]}

n = make_nameko_helper(config)

n.rpc.syncer_service.run()
