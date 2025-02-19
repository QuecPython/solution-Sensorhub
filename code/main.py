"""Simple Example for sensor data collection and report to qth server."""

import utime
from machine import I2C
from usr.libs.logging import getLogger
from usr.qth_client import QthClient
from usr.libs.threading import Thread, Lock
from usr.drivers.shtc3 import Shtc3, SHTC3_SLAVE_ADDR
from usr.drivers.lps22hb import Lps22hb, LPS22HB_SLAVE_ADDRESS
from usr.drivers.tcs34725 import Tcs34725, TCS34725_SLAVE_ADDR


logger = getLogger(__name__)


class DataSet(object):
    
    def __init__(self):
        self.temp1 = 0
        self.humi = 0
        self.press = 0
        self.temp2 = 0
        self.rgb888 = 0
        self.lock = Lock()
    
    def __enter__(self):
        self.lock.acquire()
    
    def __exit__(self, *args, **kwargs):
        self.lock.release()

    def dataShow(self):
        logger.info("data: temp1: {}, humi: {}, press: {}, temp2: {}, rgb888: 0x{:02X}".format(
            self.temp1, self.humi, self.press, self.temp2, self.rgb888
        ))


class SensorDataCollector(object):

    def __init__(self, data_set, shtc3, lps22hb, tcs34725):
        self.data_set = data_set
        self.shtc3 = shtc3
        self.lps22hb = lps22hb
        self.tcs34725 = tcs34725

        self.prev_temp1 = None
        self.prev_humi = None
        self.prev_temp2 = None
        self.prev_press = None
    
    def __call__(self, *args, **kwargs):
        # read sensor data
        while True:
            self.getSensorData()
            utime.sleep(1)

    def getSensorData(self):
        with self.data_set:
            try:
                temp1, humi = self.shtc3.getTempAndHumi()
                if self.prev_temp1 is None or abs(temp1 - self.prev_temp1) > 1:
                    self.data_set.temp1 = self.prev_temp1 = temp1
                else:
                    self.data_set.temp1 = None
                if self.prev_humi is None or abs(humi - self.prev_humi) > 1:
                    self.data_set.humi = self.prev_humi = humi
                else:
                    self.data_set.humi = None
            except Exception as e:
                logger.error("shtc3 get sensor data failed, {}".format(e))
            
            try:
                press, temp2 = self.lps22hb.getTempAndPressure()

                if self.prev_temp2 is None or abs(temp2 - self.prev_temp2) > 1:
                    self.data_set.temp2 = self.prev_temp2 = temp2
                else:
                    self.data_set.temp2 = None
                    
                if self.prev_press is None or abs(press - self.prev_press) > 1:
                    self.data_set.press = self.prev_press = press
                else:
                    self.data_set.press = None

            except Exception as e:
                logger.error("lps22hb get sensor data failed, {}".format(e))

            try:
                self.data_set.rgb888 = self.tcs34725.getRGBValue()
            except Exception as e:
                logger.error("tcs34725 get sensor data failed, {}".format(e))

            self.data_set.dataShow()


class SensorDataUploader(object):

    def __init__(self, data_set, qth_client):
        self.data_set = data_set
        self.qth_client = qth_client
    
    def sendLbs(self):
        for i in range(10):
            if self.qth_client.sendLbs():
                logger.info("upload LBS success")
                break
            utime.sleep(1)
        else:
            logger.info("upload LBS fail")

    def sendGnss(self):
        for i in range(10):
            if self.qth_client.sendGnss():
                logger.info("upload GNSS success")
                break
            utime.sleep(1)
        else:
            logger.info("upload GNSS fail")

    def __call__(self, *args, **kwargs):
        self.qth_client.start()

        # check and wait qth server ready
        for _ in range(30):
            if self.qth_client.isStatusOk():
                break
            utime.sleep(1)
        else:
            logger.error("can not connect to qth server, exist!!!")
            return
        
        self.sendLbs()
        self.sendGnss()
        while True:
            with self.data_set:
                try:
                    if self.qth_client.isStatusOk():
                        timestamp = utime.ticks_ms() // 1000
                        if timestamp % 5 == 0:
                            # rgb 每5秒上报
                            data = {
                                7: {
                                    1: (self.data_set.rgb888 >> 16) & 0xFF,
                                    2: (self.data_set.rgb888 >> 8) & 0xFF,
                                    3: self.data_set.rgb888 & 0xFF
                                }
                            }
                        if timestamp % 1 == 0:
                            # 1s 上报
                            if self.data_set.temp1 is not None:
                                data.update({3: self.data_set.temp1})
                            if self.data_set.humi is not None:
                                data.update({4: self.data_set.humi})
                            if self.data_set.temp2 is not None:
                                data.update({5: self.data_set.temp2})
                            if self.data_set.press is not None:
                                data.update({6: self.data_set.press})
                        result = self.qth_client.sendTsl(1, data)
                        logger.info("{} upload result: {}".format(type(self).__name__, result))
                        if timestamp % 1800 == 0:
                            # 每 1h 上报位置
                            result = self.sendLbs()
                            logger.info("{} upload LBS result: {}".format(type(self).__name__, result))
                        if timestamp % 60 == 0:
                            # 每 1h 上报位置
                            result = self.sendGnss()
                            logger.info("{} upload GNSS result: {}".format(type(self).__name__, result))
                    else:
                        logger.error("qth server connect error")
                except Exception as e:
                    print(e)
            utime.sleep(1)


def main():
    import checkNet
    checkNet.waitNetworkReady(30)

    import dataCall
    dataCall.setPDPContext(1, 0, 'BICSAPN', '', '', 0) #激活之前，应该先配置APN，这里配置第1路的APN
    dataCall.activate(1)

    # 数据集
    data_set = DataSet()

    # 云平台客户端
    qth_client = QthClient()

    # i2c channel 0 
    i2c_channel0 = I2C(I2C.I2C0, I2C.STANDARD_MODE)

    # SHTC3
    shtc3 = Shtc3(i2c_channel0, SHTC3_SLAVE_ADDR)
    shtc3.init()

    # LPS22HB
    lps22hb = Lps22hb(i2c_channel0, LPS22HB_SLAVE_ADDRESS)
    lps22hb.init()

    # TCS34725
    tcs34725 = Tcs34725(i2c_channel0, TCS34725_SLAVE_ADDR)
    tcs34725.init()

    # sensor data collector thread
    sensor_data_collector = Thread(target=SensorDataCollector(data_set, shtc3, lps22hb, tcs34725))
    sensor_data_collector.start()

    # upload data to qth server thread
    sensor_data_uploader = Thread(target=SensorDataUploader(data_set, qth_client))
    sensor_data_uploader.start()


if __name__ == "__main__":
    main()
