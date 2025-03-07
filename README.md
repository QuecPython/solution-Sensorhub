# 快速上手

## 硬件准备

Windows电脑一台，建议 `Win10` 系统。

一套[EC200U-EU Quecpython 标准开发板](https://python.quectel.com/doc/Getting_started/zh/evb/ec200x-evb.html)（含天线，Type-C数据线）

一张能够正常使用的SIM卡

## 环境搭建

- 下载并安装EC200EU系列模组驱动：[QuecPython_USB_Driver_Win10_ASR](https://images.quectel.com/python/2023/04/Quectel_Windows_USB_DriverA_Customer_V1.1.13.zip)。


- 下载并安装 [VSCode](https://code.visualstudio.com/)。
- 下载并解压 [QPYCom](https://images.quectel.com/python/2022/12/QPYcom_V3.6.0.zip) 工具到电脑的合适位置。
- 下载[固件包](../../solutions/SimpliKit/EC200UEUAAR05A01M08_TEST0222.zip  )。
- 下载[实验源码](https://gitee.com/dustin-wei/solution-sensorhub) 

## 硬件连接

按照下图硬件连接：

<img src="../../media/solutions/SimpliKit/EVB_link1.png" style="zoom: 25%;" /><img src="../../media/solutions/SimpliKit/EVB_link2.png" style="zoom: 20%;" />



1. 将天线连接至标识有 `LTE` 字样的天线连接座上。

2. 使用 Type-C 数据线连接开发板和电脑。

3. 在图示位置SIM1卡槽插入可用的 Nano SIM 卡



## 设备开发

- ### 开机

完成硬件连接工作后，当PWR，SCK1亮起或电脑设备管理器的端口列表出现包含Quectel USB字样的COM口，表示开机成功

<img src="../../media/solutions/SimpliKit/USB.png"  />



- ### 烧录固件包

参考[此章节](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#下载固件)，烧录[固件包](../../solutions/SimpliKit/EC200UEUAAR05A01M08_TEST0222.zip )至开发板。

- ### 脚本导入与运行

1.参考[此章节](https://python.quectel.com/doc/Getting_started/zh/first_python.html#PC与模组间的文件传输)，将源码目录下的code文件夹中的所有文件按原目录结构导入到模组文件系统中，如下图所示

<img src="../../media/solutions/SimpliKit/Qpycom.png"  />

2.参考[此章节](https://python.quectel.com/doc/Getting_started/zh/first_python.html#执行脚本文件)，执行主程序文件_main.py

3.参考[此章节](https://python.quectel.com/doc/Getting_started/zh/first_python.html#停止程序运行)，停止程序运行。

## 业务调试

### 程序启动

执行_main.py脚本后，程序开始运行，会打印拨号信息，包括拨号状态、IP地址、DNS服务器地址，设备号等

<img src="../../media/solutions/SimpliKit/drivers_data.png"  />

### 🚩 **Warning**

未插入SIM卡时，SCK1灯不会亮起，并且无法打印设备信息，插入SIM卡并重启设备后即可正常运行。

<img src="../../media/solutions/SimpliKit/sim_erro.png"  />

### 数据检测

开始运行后每1s会打印一次检测到的温度1，湿度，气压，温度2，颜色的三原色的数据,

<img src="../../media/solutions/SimpliKit/data.png"  />

### 数据更新

当检测以上4种的任一数据产生大于1或者原色产生大于150的变化时就会尝试上传云端更新数据，当上传成功时返回“send ret：True”，并且会提示是哪些数据发生了变化，APP读取云端最新数据进行数据更新。

<img src="../../media/solutions/SimpliKit/data_up.png"  />

<img src="../../media/solutions/SimpliKit/yun.png"  />

如果数据没有大于1的变化就会只在pqcom中打印当前检测的数据，不会发起上传云端。

<img src="../../media/solutions/SimpliKit/data1.png"  />

位置定位更新，当模组位移超过50米时，云端会刷新定位信息，app读取最新定位信息。

<img src="../../media/solutions/SimpliKit/gnss.png"  />

主动刷新APP数据，通过点击APP右上角刷新按键，APP会向服务器发起主动读取数据的指令，用于主动更新面板数据

<img src="../../media/solutions/SimpliKit/APP.png" style="zoom: 67%;" />

温度，湿度，气压，颜色，Lbs数据被获取成功

<img src="../../media/solutions/SimpliKit/data_get.png" style="zoom: 100%;" />