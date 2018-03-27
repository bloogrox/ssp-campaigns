import pykka
import requests
import settings
from app import logger


class SSP(pykka.ThreadingActor):
    def on_receive(self, payload):
        try:
            s = payload["subscriber"]
            s["ext_data"] = {}
            for f in payload["campaign"]["dsp"]["ext_fields"]:
                if f in s:
                    if s[f] is not None:
                        s["ext_data"][f] = str(s[f])

            data = {
                "dsp": payload["campaign"]["dsp"],
                "subscriber": s
            }

            logger.debug(f"SSP: sending data: {data}")
            resp = requests.post(settings.SSP_URL + "/sell/", json=data)

            if resp.status_code != 202:
                raise Exception("SSP response: "
                                f"{resp.status_code} {resp.content}")

            logger.debug(f"SSP: ssp response {resp.content}")
        except Exception as e:
            logger.error(f"SSP exception: {e}")
