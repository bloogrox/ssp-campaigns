import pykka
import requests
import settings
from app import logger


class SSP(pykka.ThreadingActor):
    def on_receive(self, payload):
        payload["subscriber"]["token"] = payload["subscriber"]["_id"]
        data = {
            "dsp": payload["campaign"]["dsp"],
            "subscriber": payload["subscriber"]
        }
        resp = requests.post(settings.SSP_URL + "/sell/", json=data, timeout=1)

        if resp.status_code != 202:
            raise Exception("SSP response: "
                            f"{resp.status_code} {resp.content}")

        logger.debug(f"SSP: ssp response {resp.content}")
