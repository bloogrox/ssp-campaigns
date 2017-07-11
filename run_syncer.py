from nameko.cli.shell import make_nameko_helper
from nameko.constants import AMQP_URI_CONFIG_KEY

import settings


config = {AMQP_URI_CONFIG_KEY: settings.AMQP_URI}

n = make_nameko_helper(config)

n.rpc.syncer_service.run()
