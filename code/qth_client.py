import net
import utime
import quecgnss
from usr.libs.collections import Singleton
from usr import Qth
from usr.libs.logging import getLogger


logger = getLogger(__name__)


QTH_PRODUCT_KEY = "pe16Db"
QTH_PRODUCT_SECRET = "ZGZMQWQ3QkVyN2Jm"


@Singleton
class QthClient(object):

    def __init__(self, pk=QTH_PRODUCT_KEY, ps=QTH_PRODUCT_SECRET):
        quecgnss.configSet(0,1)  # 设置定位星系为GPS+Beidou
        quecgnss.configSet(1,1)  # 输出的NMEA语句类型
        quecgnss.configSet(2,1)  # 打开AGPS
        quecgnss.configSet(4,1)  # 打开备电
        ret = quecgnss.init()
        if ret == 0:
            print('GNSS init ok.')
        else:
            print('GNSS init failed.')  
        Qth.init()
        
        Qth.setProductInfo(pk, ps)
        Qth.setServer('mqtt://iot-south.acceleronix.io:1883')
        Qth.setEventCb(
            {
                "devEvent": self.eventCallback, 
                "recvTrans": self.recvTransCallback, 
                "recvTsl": self.recvTslCallback, 
                "readTsl": self.readTslCallback, 
                "readTslServer": self.recvTslServerCallback,
                "ota": {
                    "otaPlan":self.otaPlanCallback,
                    "fotaResult":self.fotaResultCallback
                }
            }
        )

    def start(self):
        Qth.start()
    
    def stop(self):
        Qth.stop()
    
    def sendTsl(self, mode, value):
        return Qth.sendTsl(mode, value)

    def isStatusOk(self):
        return Qth.state()
    
    def sendLbs(self):
        cell_info = -1
        cell_info = net.getCellInfo()
        if cell_info != -1 and cell_info[2]:
            first_tuple = cell_info[2]
            lbs_data = "$LBS,{},{},{},{},{},0*69;".format(first_tuple[0][2],first_tuple[0][3],first_tuple[0][5],first_tuple[0][1],first_tuple[0][7])
            return Qth.sendOutsideLocation(lbs_data)
        return False
    
    @staticmethod
    def is_valid_gga_sentence(gga_sentence):
        #验证GNSS数据是否有效
        if gga_sentence.startswith('$GNGGA'):
            gga_data = gga_sentence.split(',')
            if len(gga_data) >= 15:
                fix_status = gga_data[6]
                if fix_status in ['1', '2']:
                    latitude = float(gga_data[2][:2]) + float(gga_data[2][2:]) / 60
                    longitude = float(gga_data[4][:3]) + float(gga_data[4][3:]) / 60
                    if 0 <= latitude <= 90 and 0 <= longitude <= 180:
                        return True
        return False

    def __sendGnss(self):
        if quecgnss.get_state() != 2:
            logger.error("GNSS error!")
            return False
        nmea_data = quecgnss.read(4096)
        if len(nmea_data) > 1:
            nmea_str = nmea_data[1].decode()
            # logger.info('nmea_data[1].decode(): {}'.format(nmea_data[1].decode()))
            nmea_lines = nmea_str.split("\n")
            # logger.info('nmea_lines: {}'.format(nmea_lines))
            gngga_data = None  # 初始化为 None
            
            for line in nmea_lines:
                if line.startswith("$GNGGA"):
                    gngga_data = line
                    # logger.info('gngga_data: {}'.format(gngga_data))
                    break  # 找到数据后立即退出循环
            
            if gngga_data:
                # logger.info('GNGGA数据: {}'.format(gngga_data))
                if self.is_valid_gga_sentence(gngga_data) == True:
                    Qth.sendOutsideLocation(gngga_data)  # 传递多个参数
                    return True
                else:
                    # logger.info("未找到$GNGGA数据")
                    return False
        else:
            # logger.error('数据不足以解码')
            return False  # 放在函数结尾，表示数据不足
    
    def sendGnss(self):
        for _ in range(10):
            if self.__sendGnss():
                return True
            utime.sleep(1)
        return False

    def eventCallback(self, event, result):
        logger.info("dev event:{} result:{}".format(event, result))
        if(2== event and 0 == result):
            Qth.otaRequest()

    def recvTransCallback(self, value):
        ret = Qth.sendTrans(1, value)
        logger.info("recvTrans value:{} ret:{}".format(value, ret))

    def recvTslCallback(self, value):
        logger.info("recvTsl:{}".format(value))
        for cmdId, val in value.items():
            logger.info("recvTsl {}:{}".format(cmdId, val))
    def readTslCallback(self, ids, pkgId):
        logger.info("readTsl ids:{} pkgId:{}".format(ids, pkgId))
        value=dict()
        for id in ids:
            if 1 == id:
                value[1]=180.25
            elif 2 == id:
                value[2]=30
            elif 3 == id:
                value[3]=True
        Qth.ackTsl(1, value, pkgId)

    def recvTslServerCallback(self, serverId, value, pkgId):
        logger.info("recvTslServer serverId:{} value:{} pkgId:{}".format(serverId, value, pkgId))
        Qth.ackTslServer(1, serverId, value, pkgId)

    def otaPlanCallback(self, plans):
        logger.info("otaPlan:{}".format(plans))
        Qth.otaAction(1)

    def fotaResultCallback(self, comp_no, result):
        logger.info("fotaResult comp_no:{} result:{}".format(comp_no, result))
        
    def sotaInfoCallback(self, comp_no, version, url, md5, crc):
        logger.info("sotaInfo comp_no:{} version:{} url:{} md5:{} crc:{}".format(comp_no, version, url, md5, crc))
        # 当使用url下载固件完成，且MCU更新完毕后，需要获取MCU最新的版本信息，并通过setMcuVer进行更新
        Qth.setMcuVer("MCU1", "V1.0.0", self.sotaInfoCallback, self.sotaResultCallback)

    def sotaResultCallback(comp_no, result):
        logger.info("sotaResult comp_no:{} result:{}".format(comp_no, result))
