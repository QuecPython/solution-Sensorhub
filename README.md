# quick_start



## Hardware preparation

A Windows computer, recommended 'Win10' system.

A set of [EC200U-EU Quecpython Standard Development Board](https://python.quectel.com/doc/Getting_started/zh/evb/ec200x-evb.html) (including antenna and Type-C data cable)

A functioning SIM card that is usable normally

## programming environment setup

- Download and install the EC200EU series module driver：[QuecPython_USB_Driver_Win10_ASR](https://images.quectel.com/python/2023/04/Quectel_Windows_USB_DriverA_Customer_V1.1.13.zip).
- Download and install [VSCode](https://code.visualstudio.com/).
- Download and unpack [QPYCom] (https://images.quectel.com/python/2022/12/QPYcom_V3.6.0.zip) tools to the right position of a computer.
- download [flash zip from sd card](./firmware/8915DM_cat1_open_EC200UEUAAR05A01M08_TEST0222_merge.pac).
- download [Experimental source code](https://github.com/aaronchenzhihe/solution-Sensorhub/tree/main)

## hardware connection



Follow the following diagram to connect the hardware:

<img src="./media/EVB_link1.png" style="zoom: 25%;" />[<img src="./media/EVB_link2.png" style="zoom: 20%;" />

1. Connect the antenna to the antenna connector marked with 'LTE'.

2. Use the Type-C data cable to connect the development board to the computer.

3. Insert a Nano SIM card into the SIM1 slot in the figure

## device development



- ### starting up

After the hardware connection is complete, when the PWR, SCK1 lights up or the COM port containing Quectel USB appears in the port list of the computer device Manager, it indicates that the power on is successful

[<img src="./media/USB.png"  />](https://github.com/aaronchenzhihe/solution-Sensorhub/blob/main/media/USB.png)



- ### Burn firmware package


Refer to [this section](https://python.quectel.com/doc/Application_guide/zh/dev-tools/QPYcom/qpycom-dw.html#download-firmware), and flash the [firmware package](https://github.com/aaronchenzhihe/solution-Sensorhub/solutions/SimpliKit/EC200UEUAAR05A01M08_TEST0222.zip) onto the development board.

- ### Script import and run

1.Refer to [this section](https://python.quectel.com/doc/Getting_started/zh/first_python.html#PC and module file transfer), and import all files in the code folder under the source code directory into the module file system according to the original directory structure, as shown in the following figure.

[<img src="./media/Qpycom.png"  />](https://github.com/aaronchenzhihe/solution-Sensorhub/blob/main/media/Qpycom.png)

2. Refer to [this section](https://python.quectel.com/doc/Getting_started/zh/first_python.html#executing script files), and execute the main program file _main.py

3. Refer to [this section](https://python.quectel.com/doc/Getting_started/zh/first_python.html#stop-the-program-execution), and stop the program from running.

## Service debugging



### start the application



After the _main.py script is executed, the program starts to run and prints dial-up information, including dial-up status, IP address, DNS server address, and device number

[<img src="./media/drivers_data.png"  />](https://github.com/aaronchenzhihe/solution-Sensorhub/blob/main/media/drivers_data.png)

### 🚩 **Warning**



When the SIM card is not inserted, the SCK1 light will not turn on and the device information cannot be printed. After inserting the SIM card and restarting the device, the device will run normally.

<img src="./media/sim_erro.png"  />

### data detection

After starting operation, the data of detected temperature 1, humidity, air pressure, temperature 2, and color of the three primary colors will be printed every 1s.

<img src="./media/data.png"  />

### data updating

When detecting that any of the above four types of data has a change greater than 1 or primary color has a change greater than 150, it will try to upload updated data to the cloud. When the upload is successful, "send ret: True" is returned, and it will prompt which data has changed. The APP reads the latest data from the cloud for data update.

<img src="./media/data_up.png"  />

<img src="./media/yun.png"  />

If the data does not change more than 1, only the current detected data will be printed in pqcom, and the cloud will not be uploaded.<img src="./media/data1.png"  />

Position positioning update. When the module displacement exceeds 50 meters, the cloud will refresh the positioning information, and the app will read the latest positioning information.

<img src="./media/gnss.png"  />

Actively refresh the APP data. By clicking the refresh button in the upper right corner of the APP, the APP will send an active data reading command to the server for actively updating the panel data.

<img src="./media/app.png" style="zoom: 67%;" />

Temperature, humidity, air pressure, color, Lbs data were obtained successfully.
