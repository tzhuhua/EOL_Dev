#python3.8.0 64位（python 32位要用32位的DLL）
#
from ctypes import *
import ctypes
import inspect
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QButtonGroup
from sys import argv, exit
from os import getcwd
from xlrd import open_workbook
from calibration.multhread import operationthread
import numpy as np
from calibration.anglecalibration import writeanglecalibration
from calibrationWindow import Ui_biaoding
from warning import Ui_warning
from confirm import Ui_Confirm

from calibration import snvalue
from CanOperation import canoperation

from calibration.definevariable import canvariable
from calibration.caliresultshow import MainWindowThread

# 角度标定确认按钮按下次数和标志
from calibration.definevariable import anglecalibrationpress

# 角度标定已经完成的角度个数
from calibration.definevariable import anglecalibrationcompletednum


VCI_USBCAN2 = 4
STATUS_OK = 1

ListValueID = []


class VCI_INIT_CONFIG(Structure):
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]
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

CanDLLName = './ControlCAN.dll' #把DLL放到对应的目录下
canDLL = windll.LoadLibrary('./ControlCAN.dll')
#Linux系统下使用下面语句，编译命令：python3 python3.8.0.py
#canDLL = cdll.LoadLibrary('./libcontrolcan.so')
#canDLL = cdll.LoadLibrary('./libcontrolcan.so')

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

#Warning 窗口
class WarningWindow(Ui_warning, QWidget):
    def __init__(self):
        super(WarningWindow, self).__init__()
        self.setupUi(self)

    def show_text(self, message):
        self.Warninglabel.setText(message)

def write_test_flow(Can1Variable, Can2Variable, groupCan1Info, groupCan2Info, SysCaliResult, excelSnNameVal):
    if groupCan1Info != "无" and groupCan2Info == "无":
        Can1Variable.changeOperationStatus(1)
        opCan1 = operationthread(CaliResult=SysCaliResult, CanVariable=Can1Variable, ExcelName=excelSnNameVal, channel=0, groupCanInfo=groupCan1Info)  # 实例化线程
        opCan1.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan1.start()  # 开启ta线程
    if groupCan1Info == "无" and groupCan2Info != "无":
        Can2Variable.changeOperationStatus(1)
        opCan2 = operationthread(CaliResult=SysCaliResult, CanVariable=Can2Variable, ExcelName=excelSnNameVal, channel=1, groupCanInfo=groupCan2Info)  # 实例化线程
        opCan2.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan2.start()  # 开启ta线程
    if groupCan1Info != "无" and groupCan2Info != "无":
        Can1Variable.changeOperationStatus(1)
        Can2Variable.changeOperationStatus(1)
        opCan1 = operationthread(CaliResult=SysCaliResult, CanVariable=Can1Variable, ExcelName=excelSnNameVal, channel=0, groupCanInfo=groupCan1Info)  # 实例化线程
        opCan2 = operationthread(CaliResult=SysCaliResult, CanVariable=Can2Variable, ExcelName=excelSnNameVal, channel=1, groupCanInfo=groupCan2Info)  # 实例化线程
        opCan1.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan2.daemon = False
        opCan1.start()  # 开启ta线程
        opCan2.start()

def start_can_test(groupCan1Info, groupCan2Info, SysCaliResult=None, excelSnNameVal=None):
    Can1Variable, Can2Variable, ta1, ta2 = canoperation.can_open(groupCan1Info, groupCan2Info)

    #从系统标定开始做
    if SysCaliResult != None:
        write_test_flow(Can1Variable, Can2Variable, groupCan1Info, groupCan2Info, SysCaliResult, excelSnNameVal)
    # else:
    #     write_angle_test_flow(Can1Variable, Can2Variable, groupCan1Info, groupCan2Info, excelSnNameVal)

    return Can1Variable, Can2Variable, ta1, ta2

#Confirm 窗口
class ConfirmWindow(Ui_Confirm, QWidget):
    def __init__(self, doubleCanVariable, SysCaliResult=None, AngleResult=None, SteplineEdit=None, angleCalibrationPress=None):
        super(ConfirmWindow, self).__init__()
        self.setupUi(self)
        self.groupCan1Info = 0
        self.groupCan2Info = 0
        #SN号
        self.can1SnNumber = 0
        self.can2SnNumber = 0
        #ID号
        self.groupCan1 = 0
        self.groupCan2 = 0
        # can通路
        self.doubleCanVariable = doubleCanVariable

        #雷达SN号/安装位置错误，默认值为0，1为安装错误，2为安装正确
        self.errorValue = 0
        #确认，开始测试并关闭窗口
        self.OKpushButton.clicked.connect(self.enter_test_mode)
        #取消，关闭窗口
        self.CancelpushButton.clicked.connect(self.close)

        #批次
        self.batchNum = 0
        #客户编码
        self.clientCode = 0

        #系统标定的显示窗口
        self.SysCaliResult = SysCaliResult

        #角度标定显示的窗口
        self.AngleResult = AngleResult
        self.SteplineEdit = SteplineEdit

        #只有角度标定时，判断是否开始角度标定
        self.angleCalibrationPress = angleCalibrationPress

    def show_text(self, groupCan1Info, groupCan2Info, groupCanTypeInfo, canSnNumber, groupCan1, groupCan2, batchNum, clientCode):
        self.groupCan1Info = groupCan1Info
        self.groupCan2Info = groupCan2Info
        self.groupCanTypeInfo = groupCanTypeInfo
        self.canSnNumber = canSnNumber
        self.groupCan1 = groupCan1
        self.groupCan2 = groupCan2
        self.batchNum = batchNum
        self.clientCode = clientCode
        if self.groupCanTypeInfo == 'RFRR':
            if self.groupCan1Info == '右前' and self.groupCan2Info == '右后':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1雷达安装位置为：" + groupCan1Info + '\n'  # 加的操作只能针对str类型
                strMessage += "Can2雷达安装位置为：" + groupCan2Info + '\n'
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1
        elif self.groupCanTypeInfo == 'RF':
            if self.groupCan1Info == '右前' and self.groupCan2Info == '无':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1雷达安装位置为：" + groupCan1Info + '\n'  # 加的操作只能针对str类型
                strMessage += "Can2无雷达" + '\n'
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1
        elif self.groupCanTypeInfo == 'RR':
            if self.groupCan1Info == '无' and self.groupCan2Info == '右后':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1无雷达" + '\n'
                strMessage += "Can2雷达安装位置为：" + groupCan2Info + '\n'  # 加的操作只能针对str类型
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1
        if self.groupCanTypeInfo == 'LFLR':
            if self.groupCan1Info == '左后' and self.groupCan2Info == '左前':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1雷达安装位置为：" + groupCan1Info + '\n'  # 加的操作只能针对str类型
                strMessage += "Can2雷达安装位置为：" + groupCan2Info + '\n'
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1
        elif self.groupCanTypeInfo == 'LF':
            if self.groupCan1Info == '无' and self.groupCan2Info == '左前':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1无雷达" + '\n'
                strMessage += "Can2雷达安装位置为：" + groupCan2Info + '\n'  # 加的操作只能针对str类型
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1
        elif self.groupCanTypeInfo == 'LR':
            if self.groupCan1Info == '左后' and self.groupCan2Info == '无':
                strMessage = "批次：" + batchNum + '\n'
                strMessage += "Can雷达SN号：" + canSnNumber + '\n'
                strMessage += "客户编码：" + clientCode + '\n'
                strMessage += "Can1雷达安装位置为：" + groupCan1Info + '\n'  # 加的操作只能针对str类型
                strMessage += "Can2无雷达" + '\n'
                self.errorValue = 2
            else:
                strMessage = "雷达安装类型或者安装位置出错" + '\n'
                self.errorValue = 1

        self.textBrowser.setText(strMessage)

        return self.errorValue

    def enter_test_mode(self):
        # 从系统标定开始做起
        if self.SysCaliResult != None:
            if self.errorValue == 2:
                #拼接成excel的名称
                excelSnNameVal = snvalue.create_excel_sn(self.batchNum, self.canSnNumber, self.clientCode)
                Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.groupCan1Info, self.groupCan2Info, self.SysCaliResult, excelSnNameVal)
                self.doubleCanVariable.changeCanVariable(Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal)
                #主窗口的“确认”按钮后面显示“正在测试”/“完成”
                opMainWindow = MainWindowThread(Can1Variable, Can2Variable, self.SysCaliResult, ta1=ta1, ta2=ta2)
                opMainWindow.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                opMainWindow.start()  # 开启ta线程
                #关掉自身窗口
                self.close()
            elif self.errorValue == 1:
                self.errorValue = 0
                # 关掉自身窗口
                self.close()
        else:
            # 从角度标定开始做起
            if self.errorValue == 2:
                excelSnNameVal = snvalue.create_excel_sn(self.batchNum, self.canSnNumber, self.clientCode)
                Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.groupCan1Info, self.groupCan2Info, excelSnNameVal=excelSnNameVal)
                self.doubleCanVariable.changeCanVariable(Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal)
                #开始做角度标定
                self.angleCalibrationPress.changeAngleCaliPress(1)
                #提醒可以做角度标定
                self.SteplineEdit.setText("确认做角度标定，点击“启动”")
                # 关掉自身窗口
                self.close()
            elif self.errorValue == 1:
                self.errorValue = 0
                # 关掉自身窗口
                self.close()

class MyApp(Ui_biaoding,QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)

        self.initUI()

        #通道选择
        self.channel1 = 0
        self.channel2 = 0

        #Syetem Calibration
        self.SysCaliStart.clicked.connect(self.SysCalibrationFunction)
        #Angle Calibration
        self.AngleCaliStart.clicked.connect(self.AngleCaliFunction)
        #Type99
        self.pushButtonEnd.clicked.connect(self.Type99Function)

        self.FilePath = 0
        self.cwd = getcwd()  # 获取当前程序文件位置

        self.Can1Variable = None
        self.Can2Variable = None

        #首次角度标定
        self.AngleNum = 0
        #存储左雷达值
        self.CalcAngleListLeft = []
        #存储右雷达值
        self.CalcAngleListRight = []
        #第几个角度值
        self.AngleIndex = -1
        #配置文件中的角度值
        self.row_data = 0
        self.col_data = 0
        #配置文件中的角度个数
        self.col_data_num = 0
        #存储的所有valueByte4和valueByte5的值
        self.valueByte4All = 0
        self.valueByte5All = 0
        #当前的valueByte4和valueByte5的值
        self.valueByte4 = 0
        self.valueByte5 = 0

        self.ta1 = 0
        self.ta2 = 0

        #是否做系统标定
        self.sysCaliOrNot = 0

        #雷达安装类型是否选择正确，0为默认值，1为选择错误，2为选择正确
        self.errorValue = 0

        # can通路
        self.doubleCanVariable = canvariable()

        # 按下角度确认按钮次数，0表示第一次按下，1表示第二次按下
        self.angleCalibrationPress = anglecalibrationpress()

        # 当前角度的角度标定是否做完
        self.curAngleCaliCompleted = anglecalibrationcompletednum()

        # 角度标定线程
        self.op = 0
        self.opR = 0
        self.opL = 0

    def initUI(self):
        #安装类型
        self.groupCanType = QButtonGroup(self)
        self.groupCanType.addButton(self.RFRRradioButton, 0)
        self.groupCanType.addButton(self.RFradioButton, 1)
        self.groupCanType.addButton(self.RRradioButton, 2)
        self.groupCanType.addButton(self.LFLRradioButton, 3)
        self.groupCanType.addButton(self.LFradioButton, 4)
        self.groupCanType.addButton(self.LRradioButton, 5)
        #CAN1
        self.groupCan1 = QButtonGroup(self)
        self.groupCan1.addButton(self.Can1RFradioButton, 6)
        self.groupCan1.addButton(self.Can1LRradioButton, 7)
        self.groupCan1.addButton(self.Can1NoneradioButton, 8)
        #CAN2
        self.groupCan2 = QButtonGroup(self)
        self.groupCan2.addButton(self.Can2LFradioButton, 9)
        self.groupCan2.addButton(self.Can2RRradioButton, 10)
        self.groupCan2.addButton(self.Can2NoneradioButton, 11)

        self.groupCanTypeInfo = ''
        self.groupCan1Info = ''
        self.groupCan2Info = ''

        self.groupCanType.buttonClicked.connect(self.radiobutton_clicked)
        self.groupCan1.buttonClicked.connect(self.radiobutton_clicked)
        self.groupCan2.buttonClicked.connect(self.radiobutton_clicked)

    def radiobutton_clicked(self):
        sender = self.sender()
        if sender == self.groupCanType:
            if self.groupCanType.checkedId() == 0:
                self.groupCanTypeInfo = 'RFRR'
            elif self.groupCanType.checkedId() == 1:
                self.groupCanTypeInfo = 'RF'
            elif self.groupCanType.checkedId() == 2:
                self.groupCanTypeInfo = 'RR'
            elif self.groupCanType.checkedId() == 3:
                self.groupCanTypeInfo = 'LFLR'
            elif self.groupCanType.checkedId() == 4:
                self.groupCanTypeInfo = 'LF'
            elif self.groupCanType.checkedId() == 5:
                self.groupCanTypeInfo = 'LR'
            else:
                self.groupCanTypeInfo = ''
        elif sender == self.groupCan1:
            if self.groupCan1.checkedId() == 6:
                self.groupCan1Info = '右前'
            elif self.groupCan1.checkedId() == 7:
                self.groupCan1Info = '左后'
            elif self.groupCan1.checkedId() == 8:
                self.groupCan1Info = '无'
            else:
                self.groupCan1Info = ''

        elif sender == self.groupCan2:
            if self.groupCan2.checkedId() == 9:
                self.groupCan2Info = '左前'
            elif self.groupCan2.checkedId() == 10:
                self.groupCan2Info = '右后'
            elif self.groupCan2.checkedId() == 11:
                self.groupCan2Info = '无'
            else:
                self.groupCan2Info = ''

    def SysCalibrationFunction(self):
        self.SysCaliResult.setText(None)
        self.AngleResult.setText(None)
        self.SteplineEdit.setText(None)
        self.lineEditEnd.setText(None)
        # 为1表示做了系统标定
        self.sysCaliOrNot = 1
        if self.groupCanTypeInfo == '' or self.groupCan1Info == '' or self.groupCan2Info == '':
            self.warningWindow = WarningWindow()
            self.warningWindow.show_text("Can1、Can2雷达安装位置或雷达安装类型未选择！")
            self.warningWindow.show()
        elif self.groupCanTypeInfo != '' and self.groupCan1Info != '' and self.groupCan2Info != '':
            # 这里就是获取值
            # 批次
            batchNum = self.PatchlineEdit.text()
            # SN号
            self.canSnNumber = self.SNlineEdit.text()
            # 客户编码
            clientCode = self.UserCodelineEdit.text()
            self.confirmWindow = ConfirmWindow(self.doubleCanVariable, SysCaliResult=self.SysCaliResult)
            self.confirmWindow.show_text(self.groupCan1Info, self.groupCan2Info, self.groupCanTypeInfo, self.canSnNumber,
                                         self.groupCan1, self.groupCan2, batchNum, clientCode)
            self.confirmWindow.show()

    def AngleCaliFunction(self):
        # 做完系统标定再做角度标定，为1表示做了系统标定，为2表示做了角度标定
        if self.sysCaliOrNot == 1 or self.sysCaliOrNot == 2:
            self.sysCaliOrNot = 2
            Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal = self.doubleCanVariable.getCanVariable()

            # 得到距离值
            if (self.AngleNum == 0):
                workbook = open_workbook("C:/标定/配置文件/配置文件.xls")
                worksheet = workbook.sheet_by_index(0)
                # DistanceValue = worksheet.cell_value(0, 1)
                #
                # value = int(DistanceValue * 100)
                # self.valueByte4 = value & 0xff
                # self.valueByte5 = (value & 0xff00) >> 8

                # 得到距离值
                row_dis_data = worksheet.row_values(1)
                self.row_data = row_dis_data[1:]
                self.valueByte4All = [(int(value * 100) & 0xff) for value in self.row_data]
                self.valueByte5All = [((int(value * 100) & 0xff00) >> 8) for value in self.row_data]

                # 得到角度值
                col_raw_data = worksheet.row_values(2)
                self.col_data = col_raw_data[1:]
                self.col_data_num = np.array(self.col_data).shape[0]
                # 只有第一次才读取角度
                self.AngleNum = 1

            if self.AngleIndex == -1:
                EditOutput = "当前角反距离为" + str(self.row_data[self.AngleIndex + 1]) + ",角度为" + str(
                    int(self.col_data[self.AngleIndex + 1])) + "°，确定后请按'启动'"
                self.SteplineEdit.setText(EditOutput)
                self.AngleIndex = 0
            else:
                # CurrentAngle = self.col_data[self.AngleIndex]
                # self.valueByte4 = self.valueByte4All[self.AngleIndex]
                # self.valueByte5 = self.valueByte5All[self.AngleIndex]
                # self.AngleIndex = self.AngleIndex + 1

                if self.AngleIndex == 0:
                    self.AngleIndex = 1
                    # 只有第一次做角度标定才开启线程
                    # 现在是把所有的距离角度信息都传递下去
                    if self.groupCan1Info != '无' and self.groupCan2Info == '无':  # 判断左雷达SN输入是否为空
                        # changeOperationStatus(3)表示做角度标定
                        Can1Variable.changeOperationStatus(3)
                        self.op = operationthread(CaliResult=self.AngleResult, CanVariable=Can1Variable,
                                                  AngleValue=self.col_data,
                                                  DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=0,
                                                  CalcAngleList=self.CalcAngleListLeft, ColDataNum=self.col_data_num,
                                                  CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                        self.op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                        self.op.start()  # 开启ta线程

                    if self.groupCan1Info == '无' and self.groupCan2Info != '无':  # 判断右雷达SN输入是否为空
                        Can2Variable.changeOperationStatus(3)
                        self.col_data_reverse = [val * -1. for val in self.col_data]
                        self.op = operationthread(CaliResult=self.AngleResult, CanVariable=Can2Variable,
                                                  AngleValue=self.col_data_reverse,
                                                  DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=1,
                                                  CalcAngleList=self.CalcAngleListRight, ColDataNum=self.col_data_num,
                                                  CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                        self.op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                        self.op.start()  # 开启ta线程

                    if self.groupCan1Info != '无' and self.groupCan2Info != '无':  # 判断右雷达SN输入是否为空
                        Can1Variable.changeOperationStatus(3)
                        self.opL = operationthread(CaliResult=self.AngleResult, CanVariable=Can1Variable,
                                                   AngleValue=self.col_data,
                                                   DisValue4=self.valueByte4All, DisValue5=self.valueByte5All,
                                                   channel=0,
                                                   CalcAngleList=self.CalcAngleListLeft, ColDataNum=self.col_data_num,
                                                   CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                        self.opL.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                        self.opL.start()  # 开启ta线程
                        Can2Variable.changeOperationStatus(3)
                        self.col_data_reverse = [val * -1. for val in self.col_data]
                        self.opR = operationthread(CaliResult=self.AngleResult, CanVariable=Can2Variable,
                                                   AngleValue=self.col_data_reverse,
                                                   DisValue4=self.valueByte4All, DisValue5=self.valueByte5All,
                                                   channel=1,
                                                   CalcAngleList=self.CalcAngleListRight, ColDataNum=self.col_data_num,
                                                   CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                        self.opR.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                        self.opR.start()  # 开启ta线程

                self.curAngleCaliCompleted.changeAngleCaliCompletedNum(1)

                while True:
                    # 只有左雷达
                    if self.groupCan1Info != '无' and self.groupCan2Info == '无':
                        if Can1Variable.getOperationStatus() == 4:
                            # print(self.CalcAngleListLeft)
                            if self.AngleIndex == self.col_data_num:
                                self.AngleNum = 0
                                self.SteplineEdit.setText("所有角度都测试完成")
                                # 为了下一个板子进行系统标定，角度标定测试
                                self.AngleIndex = -1
                                ExcelName = str(excelSnNameVal)
                                varPassFailCan1 = writeanglecalibration(ExcelName, self.CalcAngleListLeft, self.col_data_num,
                                                      self.groupCan1Info)
                                if varPassFailCan1 == 0:
                                    self.AngleResult.setText("Pass")
                                else:
                                    self.AngleResult.setText("方差错误，Fail")
                                # 清空存储的角度值
                                self.CalcAngleListLeft = []
                            else:
                                # 这里需要str()
                                EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                    int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                # print(EditOutput)
                                self.SteplineEdit.setText(EditOutput)
                                Can1Variable.changeOperationStatus(3)
                            break

                    # 只有右雷达
                    if self.groupCan1Info == '无' and self.groupCan2Info != '无':
                        if Can2Variable.getOperationStatus() == 4:
                            # print(self.CalcAngleListRight)
                            if self.AngleIndex == self.col_data_num:
                                self.AngleNum = 0
                                self.SteplineEdit.setText("所有角度都测试完成")
                                # 为了下一个板子进行系统标定，角度标定测试
                                self.AngleIndex = -1
                                ExcelName = str(excelSnNameVal)
                                varPassFailCan2 = writeanglecalibration(ExcelName, self.CalcAngleListRight, self.col_data_num,
                                                      self.groupCan2Info)
                                if varPassFailCan2 == 0:
                                    self.AngleResult.setText("Pass")
                                else:
                                    self.AngleResult.setText("方差错误，Fail")
                                # 清空存储的角度值
                                self.CalcAngleListRight = []
                            else:
                                # 这里需要str()
                                EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                    int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                # print(EditOutput)
                                self.SteplineEdit.setText(EditOutput)
                                Can2Variable.changeOperationStatus(3)
                            break

                    # 双雷达
                    if self.groupCan1Info != '无' and self.groupCan2Info != '无':
                        if Can1Variable.getOperationStatus() == 4 and Can2Variable.getOperationStatus() == 4:
                            # print(self.CalcAngleListLeft)
                            # print(self.CalcAngleListRight)
                            if self.AngleIndex == self.col_data_num:
                                self.AngleNum = 0
                                self.SteplineEdit.setText("所有角度都测试完成")
                                # 为了下一个板子进行系统标定，角度标定测试
                                self.AngleIndex = -1
                                ExcelName = str(excelSnNameVal)
                                varPassFailCan1 = writeanglecalibration(ExcelName, self.CalcAngleListLeft, self.col_data_num,
                                                      self.groupCan1Info)
                                ExcelName = str(excelSnNameVal)
                                varPassFailCan2 = writeanglecalibration(ExcelName, self.CalcAngleListRight, self.col_data_num,
                                                      self.groupCan2Info)
                                if varPassFailCan1 == 0 and varPassFailCan2 == 0:
                                    self.AngleResult.setText("Pass")
                                else:
                                    self.AngleResult.setText("方差错误，Fail")
                                self.angleCalibrationPress.changeAngleCaliPress(0)
                                # 清空存储的角度值
                                self.CalcAngleListLeft = []
                                self.CalcAngleListRight = []
                            else:
                                # 这里需要str()
                                EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                    int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                # print(EditOutput)
                                self.SteplineEdit.setText(EditOutput)
                                Can1Variable.changeOperationStatus(3)
                                Can2Variable.changeOperationStatus(3)
                            break
                self.AngleIndex = self.AngleIndex + 1
        else:
            # 只做角度标定
            self.sysCaliOrNot = 3
            anglePressNum = self.angleCalibrationPress.getAngleCaliPress()
            if (self.groupCanTypeInfo == '' or self.groupCan1Info == '' or self.groupCan2Info == '') and anglePressNum == 0:
                self.warningWindow = WarningWindow()
                self.warningWindow.show_text("Can1、Can2雷达安装位置或雷达安装类型未选择！")
                self.warningWindow.show()
            elif (self.groupCanTypeInfo != '' and self.groupCan1Info != '' and self.groupCan2Info != '') and anglePressNum == 0:
                # 这里就是获取值
                # 批次
                batchNum = self.PatchlineEdit.text()
                # SN号
                self.canSnNumber = self.SNlineEdit.text()
                # 客户编码
                clientCode = self.UserCodelineEdit.text()
                self.confirmWindow = ConfirmWindow(self.doubleCanVariable, AngleResult=self.AngleResult, SteplineEdit=self.SteplineEdit,
                                                   angleCalibrationPress=self.angleCalibrationPress)
                self.confirmWindow.show_text(self.groupCan1Info, self.groupCan2Info, self.groupCanTypeInfo,
                                             self.canSnNumber, self.groupCan1, self.groupCan2, batchNum, clientCode)
                self.confirmWindow.show()
            elif anglePressNum == 1:
                Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal = self.doubleCanVariable.getCanVariable()
                if (self.AngleNum == 0):
                    workbook = open_workbook("C:/标定/配置文件/配置文件.xls")
                    worksheet = workbook.sheet_by_index(0)

                    # 得到距离值
                    row_dis_data = worksheet.row_values(1)
                    self.row_data = row_dis_data[1:]
                    self.valueByte4All = [(int(value * 100) & 0xff) for value in self.row_data]
                    self.valueByte5All = [((int(value * 100) & 0xff00) >> 8) for value in self.row_data]

                    # 得到角度值
                    col_raw_data = worksheet.row_values(2)
                    self.col_data = col_raw_data[1:]
                    self.col_data_num = np.array(self.col_data).shape[0]
                    # 只有第一次才读取角度
                    self.AngleNum = 1

                if self.AngleIndex == -1:
                    EditOutput = "当前角反距离为" + str(self.row_data[self.AngleIndex + 1]) + ",角度为" + str(int(self.col_data[self.AngleIndex + 1])) + "°，确定后请按'启动'"
                    self.SteplineEdit.setText(EditOutput)
                    self.AngleIndex = 0
                else:
                    # CurrentAngle = self.col_data[self.AngleIndex]
                    # self.valueByte4 = self.valueByte4All[self.AngleIndex]
                    # self.valueByte5 = self.valueByte5All[self.AngleIndex]
                    # self.AngleIndex = self.AngleIndex + 1

                    if self.AngleIndex == 0:
                        self.AngleIndex = 1
                        # 只有第一次做角度标定才开启线程
                        # 现在是把所有的距离角度信息都传递下去
                        if self.groupCan1Info != '无' and self.groupCan2Info == '无':  # 判断左雷达SN输入是否为空
                            # changeOperationStatus(3)表示做角度标定
                            Can1Variable.changeOperationStatus(3)
                            self.op = operationthread(CaliResult=self.AngleResult, CanVariable=Can1Variable, AngleValue=self.col_data,
                                                 DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=0,
                                                 CalcAngleList=self.CalcAngleListLeft, ColDataNum=self.col_data_num,
                                                 CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                            self.op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                            self.op.start()  # 开启ta线程

                        if self.groupCan1Info == '无' and self.groupCan2Info != '无':  # 判断右雷达SN输入是否为空
                            Can2Variable.changeOperationStatus(3)
                            self.col_data_reverse = [val * -1. for val in self.col_data]
                            self.op = operationthread(CaliResult=self.AngleResult, CanVariable=Can2Variable, AngleValue=self.col_data_reverse,
                                                 DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=1,
                                                 CalcAngleList=self.CalcAngleListRight, ColDataNum=self.col_data_num,
                                                 CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                            self.op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                            self.op.start()  # 开启ta线程

                        if self.groupCan1Info != '无' and self.groupCan2Info != '无':  # 判断右雷达SN输入是否为空
                            Can1Variable.changeOperationStatus(3)
                            self.opL = operationthread(CaliResult=self.AngleResult, CanVariable=Can1Variable,
                                                  AngleValue=self.col_data,
                                                  DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=0,
                                                  CalcAngleList=self.CalcAngleListLeft, ColDataNum=self.col_data_num,
                                                  CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                            self.opL.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                            self.opL.start()  # 开启ta线程
                            Can2Variable.changeOperationStatus(3)
                            self.col_data_reverse = [val * -1. for val in self.col_data]
                            self.opR = operationthread(CaliResult=self.AngleResult, CanVariable=Can2Variable,
                                                  AngleValue=self.col_data_reverse,
                                                  DisValue4=self.valueByte4All, DisValue5=self.valueByte5All, channel=1,
                                                  CalcAngleList=self.CalcAngleListRight, ColDataNum=self.col_data_num,
                                                  CurAngleCaliCompleted=self.curAngleCaliCompleted)  # 实例化线程
                            self.opR.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
                            self.opR.start()  # 开启ta线程

                    self.curAngleCaliCompleted.changeAngleCaliCompletedNum(1)

                    while True:
                        # 只有左雷达
                        if self.groupCan1Info != '无' and self.groupCan2Info == '无':
                            if Can1Variable.getOperationStatus() == 4:
                                # print(self.CalcAngleListLeft)
                                if self.AngleIndex == self.col_data_num:
                                    self.AngleNum = 0
                                    self.SteplineEdit.setText("所有角度都测试完成")
                                    # 为了下一个板子进行系统标定，角度标定测试
                                    self.AngleIndex = -1
                                    ExcelName = str(excelSnNameVal)
                                    varPassFailCan1 = writeanglecalibration(ExcelName, self.CalcAngleListLeft, self.col_data_num,
                                                          self.groupCan1Info)
                                    if varPassFailCan1 == 0:
                                        self.AngleResult.setText("Pass")
                                    else:
                                        self.AngleResult.setText("方差错误，Fail")
                                    self.angleCalibrationPress.changeAngleCaliPress(0)
                                    # 清空存储的角度值
                                    self.CalcAngleListLeft = []
                                else:
                                    # 这里需要str()
                                    EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                        int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                    # print(EditOutput)
                                    self.SteplineEdit.setText(EditOutput)
                                    Can1Variable.changeOperationStatus(3)
                                break

                        # 只有右雷达
                        if self.groupCan1Info == '无' and self.groupCan2Info != '无':
                            if Can2Variable.getOperationStatus() == 4:
                                # print(self.CalcAngleListRight)
                                if self.AngleIndex == self.col_data_num:
                                    self.AngleNum = 0
                                    self.SteplineEdit.setText("所有角度都测试完成")
                                    # 为了下一个板子进行系统标定，角度标定测试
                                    self.AngleIndex = -1
                                    ExcelName = str(excelSnNameVal)
                                    varPassFailCan2 = writeanglecalibration(ExcelName, self.CalcAngleListRight, self.col_data_num,
                                                          self.groupCan2Info)
                                    if varPassFailCan2 == 0:
                                        self.AngleResult.setText("Pass")
                                    else:
                                        self.AngleResult.setText("方差错误，Fail")
                                    self.angleCalibrationPress.changeAngleCaliPress(0)
                                    # 清空存储的角度值
                                    self.CalcAngleListRight = []
                                else:
                                    # 这里需要str()
                                    EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                        int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                    # print(EditOutput)
                                    self.SteplineEdit.setText(EditOutput)
                                    Can2Variable.changeOperationStatus(3)
                                break

                        # 双雷达
                        if self.groupCan1Info != '无' and self.groupCan2Info != '无':
                            if Can1Variable.getOperationStatus() == 4 and Can2Variable.getOperationStatus() == 4:
                                # print(self.CalcAngleListLeft)
                                # print(self.CalcAngleListRight)
                                if self.AngleIndex == self.col_data_num:
                                    self.AngleNum = 0
                                    self.SteplineEdit.setText("所有角度都测试完成")
                                    # 为了下一个板子进行系统标定，角度标定测试
                                    self.AngleIndex = -1
                                    ExcelName = str(excelSnNameVal)
                                    varPassFailCan1 = writeanglecalibration(ExcelName, self.CalcAngleListLeft, self.col_data_num,
                                                          self.groupCan1Info)
                                    ExcelName = str(excelSnNameVal)
                                    varPassFailCan2 = writeanglecalibration(ExcelName, self.CalcAngleListRight, self.col_data_num,
                                                          self.groupCan2Info)
                                    if varPassFailCan1 == 0 and varPassFailCan2 == 0:
                                        self.AngleResult.setText("Pass")
                                    else:
                                        self.AngleResult.setText("方差错误，Fail")
                                    self.angleCalibrationPress.changeAngleCaliPress(0)
                                    # 清空存储的角度值
                                    self.CalcAngleListLeft = []
                                    self.CalcAngleListRight = []
                                else:
                                    # 这里需要str()
                                    EditOutput = "请把角反放在" + str(self.row_data[self.AngleIndex]) + " m，" + str(
                                        int(self.col_data[self.AngleIndex])) + "°位置，再按'启动'"
                                    # print(EditOutput)
                                    self.SteplineEdit.setText(EditOutput)
                                    Can1Variable.changeOperationStatus(3)
                                    Can2Variable.changeOperationStatus(3)
                                break
                    self.AngleIndex = self.AngleIndex + 1

    def Type99Function(self):
        # 为1/2表示做了系统/角度标定
        if self.sysCaliOrNot == 1 or self.sysCaliOrNot == 2 or self.sysCaliOrNot == 3:
            Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal = self.doubleCanVariable.getCanVariable()
            self.sysCaliOrNot = 0
        elif self.sysCaliOrNot == 0:
            Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.groupCan1Info, self.groupCan2Info)

        self.lineEditEnd.setText("正在测试")
        ubyte_array = c_ubyte * 8
        a = ubyte_array(0xC1, 0x99, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)
        ubyte_3array = c_ubyte * 3
        b = ubyte_3array(0, 0, 0)
        vci_can_obj = VCI_CAN_OBJ(0x635, 0, 0, 1, 0, 0, 8, a, b)  # 单次发送

        if self.groupCan1Info != '无':  # 判断左雷达SN输入是否为空
            Can1Variable.changeOperationStatus(5)
            ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, 0, byref(vci_can_obj), 1)
            #if ret == STATUS_OK:
            #    print('CAN1通道发送成功\r\n')
            #if ret != STATUS_OK:
            #    print('CAN1通道发送失败\r\n')

            op = operationthread(CanVariable=Can1Variable)  # 实例化线程
            op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
            op.start()  # 开启ta线程

        if self.groupCan2Info != '无':  # 判断右雷达SN输入是否为空
            Can2Variable.changeOperationStatus(5)
            ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, 1, byref(vci_can_obj), 1)
            #if ret == STATUS_OK:
            #    print('CAN2通道发送成功\r\n')
            #if ret != STATUS_OK:
            #    print('CAN2通道发送失败\r\n')

            op = operationthread(CanVariable=Can2Variable)  # 实例化线程
            op.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
            op.start()  # 开启ta线程

        while (True):
            # 只有左雷达
            if self.groupCan1Info != '无' and self.groupCan2Info == '无':
                if Can1Variable.getOperationStatus() == 6:
                    self.lineEditEnd.setText("Pass")
                    break
                elif Can1Variable.getOperationStatus() == 7:
                    self.lineEditEnd.setText("Fail")
                    break
                else:
                    self.lineEditEnd.setText("Pass")
                    break

            # 只有右雷达
            if self.groupCan1Info == '无' and self.groupCan2Info != '无':
                if Can2Variable.getOperationStatus() == 6:
                    self.lineEditEnd.setText("Pass")
                    break
                elif Can2Variable.getOperationStatus() == 7:
                    self.lineEditEnd.setText("Fail")
                    break
                else:
                    self.lineEditEnd.setText("Pass")
                    break

            # 双雷达
            if self.groupCan1Info != '无' and self.groupCan2Info != '无':
                if Can1Variable.getOperationStatus() == 6 and Can2Variable.getOperationStatus() == 6:
                    self.lineEditEnd.setText("Pass")
                    break
                else:
                    if Can1Variable.getOperationStatus() == 7 or Can2Variable.getOperationStatus() == 7:
                        self.lineEditEnd.setText("Fail")
                        break
                    else:
                        self.lineEditEnd.setText("Fail")
                        break


        canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
        if ta1 != 0:
            stop_thread(ta1)
        if ta2 != 0:
            stop_thread(ta2)

if __name__ == "__main__":
    app = QApplication(argv)
    window = MyApp()
    window.show()
    exit(app.exec_())














