import threading
from ctypes import *
import numpy as np
from .systemcalibration import syscalibration
from .anglecalibration import anglecalibration
from .type99 import type99
from .createdoc import CreateWorkbook
from .createdoc import CloseWorkbook
from xlrd import open_workbook
import time
import os
from StatusShow import statusdisplay
import csv
import global_variable as gv
gv.set_variable('save_can_text_flag', False)
VCI_USBCAN2 = 4
STATUS_OK = 1

class VCI_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ]

CanDLLName = os.path.join(os.getcwd(), 'ControlCAN.dll') #把DLL放到对应的目录下
canDLL = windll.LoadLibrary(CanDLLName)

class mythread(threading.Thread):
    def __init__(self, channel, CanVariable):
        threading.Thread.__init__(self)
        self.channel = channel
        self.CanVariable = CanVariable

    def run(self):
        #ListValueMessage = []

        ubyte_array = c_ubyte * 8
        a = ubyte_array(0, 0, 0, 0, 0, 0, 0, 0)
        ubyte_3array = c_ubyte * 3
        b = ubyte_3array(0, 0, 0)
        vci_can_obj = VCI_CAN_OBJ(0x0, 0, 0, 0, 0, 0, 0, a, b)  # 复位接收缓存

        while (True):
            ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 1, 0)    #每次接收一帧数据，这里设为1
            while ret <= 0:  # 如果没有接收到数据，一直循环查询接收。
                ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 1, 0)
            if ret > 0:  # 接收到一帧数据
                print(vci_can_obj.DataLen)
                print(list(vci_can_obj.Data))

                #剔除掉心跳报文
                if vci_can_obj.ID != 0x600:
                    StoreValue = []
                    StoreValue.append(vci_can_obj.ID)
                    for value in list(vci_can_obj.Data):
                        StoreValue.append(value)
                    #ListValueMessage.append(StoreValue)
                    self.CanVariable.appendListValueMessage(StoreValue)
                    #print(np.array(self.CanVariable.getListValueMessage()).shape[0])
                    #print(vci_can_obj.ID)
            #         # print(vci_can_obj.TimeStamp)
            #         # time_local = time.localtime(vci_can_obj.TimeStamp)
            #         # dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            #         # print(dt)
            # vci_can_obj.ID = 0

class operationthread(threading.Thread):
    def __init__(self, CaliResult=None, CanVariable=None, ExcelName=None, channel=None, AngleValue=None, DisValue4=None,
                 DisValue5=None, CalcAngleList=None, groupCanInfo=None, ColDataNum=None, CurAngleCaliCompleted=None):
        threading.Thread.__init__(self)
        self.CaliResult = CaliResult
        self.CanVariable = CanVariable
        self.ExcelName = ExcelName
        self.channel = channel
        self.AngleValue = AngleValue
        self.DisValue4 = DisValue4
        self.DisValue5 = DisValue5
        self.CalcAngleList = CalcAngleList
        self.groupCanInfo = groupCanInfo
        self.ColDataNum = ColDataNum
        self.CurAngleCaliCompleted = CurAngleCaliCompleted

    def run(self):
        OperationStatus = self.CanVariable.getOperationStatus()
        name = gv.get_variable('can_log')

        #系统标定
        if OperationStatus == 1:
            # 得到距离值
            workbook = open_workbook(gv.get_variable("biaoding_wenjian"))
            worksheet = workbook.sheet_by_index(0)
            DistanceValue = worksheet.cell_value(0, 1)

            value = int(DistanceValue * 100)
            valueByte4 = value & 0xff
            valueByte5 = (value & 0xff00) >> 8

            ubyte_array = c_ubyte * 8
            a = ubyte_array(0xC1, 0x51, 0x5B, 0x05, valueByte4, valueByte5, 0x0A, 0x0)
            ubyte_3array = c_ubyte * 3
            b = ubyte_3array(0, 0, 0)
            vci_can_obj = VCI_CAN_OBJ(0x635, 0, 0, 1, 0, 0, 8, a, b)  # 单次发送
            ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 1)
            # 发送指令起始时间
            gv.set_variable('save_can_text_flag', True)
            print("sended")
            timeStartVal = time.time()

            while True:
                ListValueMessage = self.CanVariable.getListValueMessage()
                timeEndVal = time.time()
                if np.array(ListValueMessage).shape[0] > 190:  # 这里接收的数据长度要注意，现在为190 187
                    wb = CreateWorkbook()
                    # print(ListValueMessage)
                    result = syscalibration(self.CaliResult, wb, self.CanVariable)
                    self.CanVariable.changeOperationStatus(2)
                    if result != "成功":
                        self.CanVariable.changeAnalyseError(result)
                    else:
                        # print(self.CanVariable.getListValueMessage())
                        self.CanVariable.clearListValueMessage()
                        CloseWorkbook(wb, self.ExcelName, self.groupCanInfo)  # 保存
                        gv.set_variable('save_can_text_flag', False)
                    break
                # 大于60s就终止系统标定
                if (timeEndVal - timeStartVal) > 60:
                    self.CanVariable.changeOperationStatus(2)
                    self.CanVariable.changeTimeOutVal(1)
                    # canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
                    gv.set_variable('save_can_text_flag', False)
                    break
        #角度标定
        if OperationStatus == 3:
            AngleIndex = 0
            while True:
                while True:
                    curAngleCompletedOrNot = self.CurAngleCaliCompleted.getAngleCaliCompletedNum()
                    # 1 表示按键按下，准备好做角度标定，0表示还没有准备好做角度标定
                    if curAngleCompletedOrNot == 1:
                        break

                CurrentAngle = self.AngleValue[AngleIndex]
                valueByte4 = self.DisValue4[AngleIndex]
                valueByte5 = self.DisValue5[AngleIndex]
                AngleIndex = AngleIndex + 1

                ColData = int(CurrentAngle)
                ubyte_array = c_ubyte * 8
                a = ubyte_array(0xC1, 0x52, 0x5B, 0x05, valueByte4, valueByte5, 0x0a, ColData)
                ubyte_3array = c_ubyte * 3
                b = ubyte_3array(0, 0, 0)
                vci_can_obj = VCI_CAN_OBJ(0x635, 0, 0, 1, 0, 0, 8, a, b)  # 单次发送

                ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 1)
                gv.set_variable('save_can_text_flag', True)

                # 发送指令起始时间
                timeStartVal = time.time()

                if ret == STATUS_OK:
                    # print('CAN1通道发送成功\r\n')
                    while True:
                        timeEndVal = time.time()
                        ListValueMessage = self.CanVariable.getListValueMessage()
                        if np.array(ListValueMessage).shape[0] == 7:  # 接收到角度标定的数据长度，这里为7
                            anglecalibration(ListValueMessage, self.CalcAngleList)
                            self.CanVariable.clearListValueMessage()
                            self.CanVariable.changeOperationStatus(4)
                            gv.set_variable('save_can_text_flag', False)
                            break
                        # 大于60s就终止系统标定
                        if (timeEndVal - timeStartVal) > 60:
                            self.CanVariable.changeOperationStatus(4)
                            self.CanVariable.changeTimeOutVal(1)
                            # canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
                            gv.set_variable('save_can_text_flag', False)
                            break
                    # 表明主界面可以进行再一次点击角度标定
                    self.CurAngleCaliCompleted.changeAngleCaliCompletedNum(0)

                # 表明角度标定完成
                if AngleIndex == self.ColDataNum:
                    break


        #type99
        if OperationStatus == 5:
            timeStartVal = time.time()
            while True:
                timeEndVal = time.time()
                ListValueMessage = self.CanVariable.getListValueMessage()
                if np.array(ListValueMessage).shape[0] == 1:
                    type99(ListValueMessage, self.CanVariable)
                    self.CanVariable.changeOperationStatus(6)
                    break
                # 大于10s就终止系统标定
                if (timeEndVal - timeStartVal) > 5:
                    self.CanVariable.changeOperationStatus(7)
                    break




class targetvaluethread(threading.Thread):
    def __init__(self, CanVariable=None, targetShowValue=None):
        threading.Thread.__init__(self)
        self.CanVariable = CanVariable
        self.targetShowValue = targetShowValue

    def run(self):
        while(True):
            # 处理需要显示的点击
            message70ACompleted = self.CanVariable.getmessage70ACompleted()
            if message70ACompleted == 2:
                # 获取target信息
                ClusterMessageValueResult = self.CanVariable.getClusterMessageValueResult()
                statusdisplay.analysisTargetRawData(self.targetShowValue, ClusterMessageValueResult)
                self.CanVariable.clearClusterMessageValueResult()
                self.CanVariable.writeMessage70ACompletedVal(1)
