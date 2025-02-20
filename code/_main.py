import net
import utime
import checkNet
from misc import Power
from usr.libs import Application
from usr.libs.logging import getLogger
from usr.extensions import (
    qth_client,
    gnss_service,
    lbs_service,
    sensor_service,
)


logger = getLogger(__name__)


def wait_network_ready():
    for _ in range(3):
        logger.info("wait network ready...")
        code = checkNet.waitNetworkReady(60)
        if code == (3, 1):
            logger.info("network has been ready.")
            break
        else:
            logger.warn("network not ready, code: {}".format(code))
            net.setModemFun(0, 0)
            utime.sleep_ms(200)
            net.setModemFun(1, 0)
    else:
        logger.warn("power restart")
        Power.powerRestart()


def create_app(name="SimpliKit", version="1.0.0", config_path="/usr/config.json"):
    _app = Application(name, version)
    _app.config.init(config_path)

    qth_client.init_app(_app)
    gnss_service.init_app(_app)
    lbs_service.init_app(_app)
    sensor_service.init_app(_app)

    return _app


if __name__ == "__main__":
    wait_network_ready()
    app = create_app()
    app.run()
