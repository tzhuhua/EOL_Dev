#python3.8.0 64位（python 32位要用32位的DLL）
#
from queue import Queue
import datetime
import  time
import pyqtgraph as pg
from threading import Timer
import global_variable as gv
gv._init()
gv.set_variable('status_flag', False)
from calibration.definevariable import definevariable
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from ctypes import *
import ctypes
import inspect
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QButtonGroup
from sys import argv, exit
from os import getcwd
import os
from xlrd import open_workbook
from calibration.multhread import operationthread
import numpy as np
from calibration.anglecalibration import writeanglecalibration
from calibrationWindow import Ui_biaoding
from warning import Ui_warning
from confirm import Ui_Confirm
from StatusShow import statusdisplay

from calibration import snvalue

from calibration.definevariable import canvariable
from calibration.caliresultshow import MainWindowThread

# 角度标定确认按钮按下次数和标志
from calibration.definevariable import anglecalibrationpress

# 角度标定已经完成的角度个数
from calibration.definevariable import anglecalibrationcompletednum
import math
from StatusShow import targetstatus

#存储处理数据的线程
from calibration.definevariable import operationthreadvariables

from calibration.definevariable import targetshowvalue

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
gv.set_variable('dll', canDLL)

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

def write_test_flow(Can1Variable, Can2Variable, SysCaliResult, excelSnNameVal, can_num):
    if Can1Variable and can_num==1:
        Can1Variable.changeOperationStatus(1)
        opCan1 = operationthread(CaliResult=SysCaliResult, CanVariable=Can1Variable, ExcelName=excelSnNameVal, channel=0)  # 实例化线程
        opCan1.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan1.start()  # 开启ta线程
    if Can2Variable and can_num==2:
        Can2Variable.changeOperationStatus(1)
        opCan2 = operationthread(CaliResult=SysCaliResult, CanVariable=Can2Variable, ExcelName=excelSnNameVal, channel=1)  # 实例化线程
        opCan2.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan2.start()  # 开启ta线程

def start_can_test(SysCaliResult=None, excelSnNameVal=None, can_num=None):
    # Can1Variable, Can2Variable, ta1, ta2 = canoperation.can_open(groupCan1Info, groupCan2Info)
    Can1Variable = gv.get_variable("Can1Variable")
    Can2Variable = gv.get_variable("Can2Variable")
    ta1 = gv.get_variable("ta1")
    ta2 = gv.get_variable("ta2")
    #从系统标定开始做
    if SysCaliResult != None:
        write_test_flow(Can1Variable, Can2Variable, SysCaliResult, excelSnNameVal, can_num)
    # else:
    #     write_angle_test_flow(Can1Variable, Can2Variable, groupCan1Info, groupCan2Info, excelSnNameVal)

    return Can1Variable, Can2Variable, ta1, ta2

#Confirm 窗口
class ConfirmWindow(Ui_Confirm, QWidget):
    def __init__(self, doubleCanVariable, SysCaliResult=None, AngleResult=None, SteplineEdit=None, angleCalibrationPress=None, can =None):
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
        self.can_num = can
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
    def show_text(self):
        strMessage = "启动系统标定？"
        self.textBrowser.setText(strMessage)
        return self.errorValue

    def enter_test_mode(self):
        # 从系统标定开始做起
        if self.SysCaliResult != None:
            #拼接成excel的名称
            excelSnNameVal = snvalue.create_excel_sn()
            Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.SysCaliResult, excelSnNameVal, self.can_num)
            self.doubleCanVariable.changeCanVariable(Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal)
            #主窗口的“确认”按钮后面显示“正在测试”/“完成”
            opMainWindow = MainWindowThread(Can1Variable, Can2Variable, self.SysCaliResult, ta1=ta1, ta2=ta2, can_num=self.can_num)
            opMainWindow.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
            opMainWindow.start()  # 开启ta线程
            #关掉自身窗口
            self.close()
        else:
            # 从角度标定开始做起
            excelSnNameVal = snvalue.create_excel_sn()
            Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.groupCan1Info, self.groupCan2Info, excelSnNameVal=excelSnNameVal)
            self.doubleCanVariable.changeCanVariable(Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal)
            #开始做角度标定
            self.angleCalibrationPress.changeAngleCaliPress(1)
            #提醒可以做角度标定
            self.SteplineEdit.setText("确认做角度标定，点击“启动”")
            # 关掉自身窗口
            self.close()


class Refresh(QThread):
    def __init__(self, ax, fig):
        super().__init__()
        self.ax = ax
        self.fig = fig
        self.figure = fig
    def run(self):
        # print(targets[0], targets[1])
        while True:
            target = gv.get_variable('target')
            if target:
                time.sleep(0.01)
                self.ax.cla()
                self.ax.set_thetagrids(np.arange(-90, 91, 10.0))
                self.ax.set_theta_zero_location('N')
                self.ax.set_theta_direction(1)
                self.ax.set_thetamin(-90)  # 设置极坐标图开始角度为0°
                self.ax.set_thetamax(90)  # 设置极坐标结束角度为180°
                self.ax.set_rgrids(np.arange(0, 61.0, 20.0))
                self.ax.set_rlim(0.0, 60.0)  # 标签范围为[0, 100)
                self.ax.set_yticklabels(['0', '20', '40', '60'])
                self.ax.grid(True, linestyle="-", color="k", linewidth=0.5, alpha=0.5)
                self.ax.set_axisbelow('False')  # 使散点覆盖在坐标系之上
                self.ax.set_rlabel_position(0)  # 标签显示在0°
                self.ax.scatter(target[0], target[1], s=5.0)
                # ax.scatter([random.uniform(0, 5) for i in range(10)], [random.uniform(0, 80) for i in range(10)], s=5.0)
                self.figure.canvas.draw()
                self.figure.canvas.flush_events()

class CanThrerad(QThread):
    text = pyqtSignal(object)
    analyse_frame = pyqtSignal(object)
    # draw = pyqtSignal(list)
    def __init__(self, channel, CanVariable):
        super().__init__()
        self.cluster_list = [[],[],[]]
        self.channel = channel
        self.CanVariable = CanVariable
        self.ta1 = 0
        self.ta2 = 0


    def run(self):
        VCI_USBCAN2A = 4
        STATUS_OK = 1

        class VCI_INIT_CONFIG(Structure):
            _fields_ = [("AccCode", c_ulong),
                        ("AccMask", c_ulong),
                        ("Reserved", c_ulong),
                        ("Filter", c_ubyte),
                        ("Timing0", c_ubyte),
                        ("Timing1", c_ubyte),
                        ("Mode", c_ubyte)
                        ]
        fild = []
        for i in range(2000):
            temp = [("ID" + str(1+i), c_uint),
                    ("TimeStamp" + str(1+i), c_uint),
                    ("TimeFlag" + str(1+i), c_ubyte),
                    ("SendType" + str(1+i), c_ubyte),
                    ("RemoteFlag" + str(1+i), c_ubyte),
                    ("ExternFlag" + str(1+i), c_ubyte),
                    ("DataLen" + str(1+i), c_ubyte),
                    ("Data" + str(1+i), c_ubyte * 8),
                    ("Reserved" + str(1+i), c_ubyte * 3)
                    ]
            fild = fild + temp


        class VCI_CAN_OBJ(Structure):
            _fields_ = fild
        canDLL = gv.get_variable('dll')
        ret = canDLL.VCI_OpenDevice(VCI_USBCAN2A, 0, 0)
        if ret != STATUS_OK:
            print('调用 VCI_OpenDevice出错\r\n')

        # 初始化通道
        vci_initconfig = VCI_INIT_CONFIG(0x80000008, 0xFFFFFFFF, 0, 2, 0x00, 0x1C, 0)
        ret = canDLL.VCI_InitCAN(VCI_USBCAN2A, 0, self.channel, byref(vci_initconfig))
        if ret != STATUS_OK:
            print('调用 VCI_InitCAN出错\r\n')
            return

        ret = canDLL.VCI_StartCAN(VCI_USBCAN2A, 0, self.channel)
        if ret != STATUS_OK:
            print('调用 VCI_StartCAN出错\r\n')
            return

        # # 通道0发送数据
        # ubyte_array = c_ubyte * 8
        # self.array = ubyte_array(0xC1, 0x51, 0x5B, 0x05, 0x64, 0x00, 0x0A, 0x0)
        # a = self.array
        # ubyte_3array = c_ubyte * 3
        # b = ubyte_3array(0, 0, 0)
        # vci_can_obj = VCI_CAN_OBJ(0x635, 0, 0, 1, 0, 0, 8, a, b)

        # ret = canDLL.VCI_Transmit(VCI_USBCAN2A, 0, 0, byref(vci_can_obj), 1)

        ubyte_array = c_ubyte * 8
        ubyte_3array = c_ubyte * 3
        a = ubyte_array(0, 0, 0, 0, 0, 0, 0, 0)
        b = ubyte_3array(0, 0, 0)
        # ret = canDLL.VCI_Receive(VCI_USBCAN2A, 0, 0, byref(vci_can_obj), 1, 0)
        name = "can_log_"+time.strftime('%H%M%S')+".csv"
        gv.set_variable('can_log', name)
        while True:
            analyse_flag = False
            vci_can_obj = VCI_CAN_OBJ(*(0x0, 0, 0, 1, 0, 0, 8, a, b) * 2000)
            ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 2000, 0)    #每次接收一帧数据，这里设为1
            # while ret <= 0:  # 如果没有接收到数据，一直循环查询接收。
            #     ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), 100, 400)
            if ret > 0:
                time_now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

                # num = canDLL.VCI_GetReceiveNum(VCI_USBCAN2A, 0, 1)
                # print(num)
                # id= vci_can_obj.ID1
                # data = list(vci_can_obj.Data1)
                frame = []
                if gv.get_variable("can_data_to_radar") != "":
                    frame.extend(gv.get_variable("can_data_to_radar"))
                    gv.set_variable("can_data_to_radar", "")
                for i in range(100):
                    vci_ID = "vci_can_obj.ID"
                    vci_Data = "vci_can_obj.Data"
                    vci_ID = vci_ID + str(i + 1)
                    vci_Data = vci_Data + str(i + 1)
                    # print(vci_ID)
                    id = eval(vci_ID)
                    data = eval(vci_Data)
                    if id != 0x0:
                        can_frame = ' '.join([hex(x)[2:].upper().zfill(2) for x in data])
                        frame.extend([[time_now, 'from radar', hex(id).upper(), can_frame]])
                        if id == 0x7F8:
                            self.CanVariable.setTargetStatusMessage(list(data))
                        if gv.get_variable('save_can_text_flag'):
                            StoreValue = []
                            StoreValue.append(id)
                            for value in list(data):
                                StoreValue.append(value)
                            # ListValueMessage.append(StoreValue)
                            self.CanVariable.appendListValueMessage(StoreValue)
                        if id == 0x70B:
                            bin_can_frame_list = [bin(x)[2:].zfill(8) for x in data]
                            bin_can_frame_str = ''.join(bin_can_frame_list)
                            ID = int(bin_can_frame_str[0:8], 2)
                            DistLong = int(bin_can_frame_str[8:18], 2) * 0.2 - 102
                            DistLat = int(bin_can_frame_str[18:28], 2) * 0.2 - 102
                            # VrelLong = int(bin_can_frame_str[28:38], 2) * 0.25 - 128
                            # VrelLat = int(bin_can_frame_str[38:47], 2) * 0.25 - 64
                            # Status = (int(bin_can_frame_str[50:53], 2))
                            # PossibilitofExist = (int(bin_can_frame_str[53:56], 2))
                            # RCS = int(bin_can_frame_str[56:64], 2) * 0.5 - 64
                            # # print(ID)
                            # # print(DistLong)
                            # # print(DistLat)
                            # # print(VrelLong)
                            # # print(VrelLat)
                            # # print(Status)
                            # # print(PossibilitofExist)
                            # # print(RCS)
                            theta = math.atan2(DistLat, DistLong)
                            r = math.sqrt(DistLong * DistLong + DistLat * DistLat)
                            self.cluster_list[0].extend([theta])
                            self.cluster_list[1].extend([r])
                        if id == 0x70A:
                            gv.set_variable('target', self.cluster_list)
                            self.cluster_list = [[], []]
                        if id == 0x7EA or id == 0x7EE:
                            analyse_flag = True
                    else:
                        break

                self.text.emit(frame)
                if analyse_flag:
                    self.analyse_frame.emit(frame)
                # with open (name, 'a', newline="") as can_log_file:
                #     writer = csv.writer(can_log_file)
                #     writer.writerow([time.strftime("%Y-%m-%d %H-%M-%S"), hex(id), data])

                # dd = canDLL.VCI_ClearBuffer(VCI_USBCAN2A, 0, 1)

class MyApp(Ui_biaoding,QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.ax = None
        self.queue_targets= Queue()
        gv.set_variable('target', [])
        self.cluster_list = [[], [], []]

        #通道选择
        self.channel1 = 0
        self.channel2 = 0

        #Syetem Calibration
        self.SysCaliStart.clicked.connect(self.SysCalibrationFunction)
        #Angle Calibration
        self.AngleCaliStart.clicked.connect(self.AngleCaliFunction)
        #Target Status
        self.statuspushButton.clicked.connect(self.TargetStatusFunction)
        #扩展模式
        self.comboBox_radar_type.currentTextChanged.connect(self.radar_type)
        self.pushButton_biaoding_history.clicked.connect(self.read_history)
        self.pushButton_start_biaoding.clicked.connect(self.run_biaoding)
        self.pushButton_read_biaoding_value.clicked.connect(self.read_value)
        self.pushButton_flash.clicked.connect(self.read_flash)
        self.pushButton_delete.clicked.connect(self.delete_flash_area)
        self.FilePath = 0
        self.cwd = getcwd()  # 获取当前程序文件位置

        self.Can1Variable = None
        self.Can2Variable = None
        self.CanVariable = None
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
        # self.can_live = Thread(target=self.show_CanText)
        # self.can_live.setDaemon(True)
        # self.can_live.start()

        # 存储处理数据的线程
        self.operationThreadVariables = operationthreadvariables()

        self.timer = 0

        self.targetShowValue = targetshowvalue()

        #保存target旧值
        self.targetShowValueOld = 0
        #第一次显示cluster
        self.firstTimeDisplay = 0

        #保存旧值
        self.TargetStatusMessageOld = []
        self.canSelectcomboBox.currentTextChanged.connect(self.get_current_can)
        self.can_num = 0
        self.thread_list = []
        self.get_current_can()

        gv.set_variable('can_data_to_radar', "")
        self.progress_ask_flag = False
        self.current_radar_type = '角雷达'
        self.progressBar.setValue(0)
        self.label_history.setText("标定历史")
        self.label_biaoding_value.setText("标定结果")
        self.read_current_value = 0
        self.flash_flag = ""
        self.bin_file_name = ""
        self.flash_frame_nums = 0
    def closeEvent(self, event):
        """
        对MainWindow的函数closeEvent进行重构
        退出软件时结束所有进程
        :param event:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '标定程序',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            dll = gv.get_variable('dll')
            dll.VCI_CloseDevice(4, 0)
            event.accept()
            os._exit(0)
        else:
            event.ignore()
    """
    各种动态标定指令
    """
    def change_flag(self, flag_type):
        if flag_type == 'read_value':
            self.read_current_value = 0
        if flag_type == 'flash_delete':
            self.flash_flag = ""
            if "正在" in self.label_delete_state.text():
                self.label_delete_state.setText("擦除数据失败！")
        if flag_type == 'flash_read':
            self.flash_flag = ""
            if "正在读取" or "读取完成 "in self.label_read_state.text():
                pass
            else:
                self.label_read_state.setText("读取数据失败！")
    def read_value(self):
        targetstatus.dongtai_biaoding(self.can_num, "value")
        self.read_current_value = 1
        reader_value = Timer(2, self.change_flag, ('read_value', ))
        reader_value.start()

    def read_history(self):
        targetstatus.dongtai_biaoding(self.can_num, "history")

    def run_biaoding(self):
        targetstatus.dongtai_biaoding(self.can_num, "kuozhan")
        self.progress_ask_flag = True

    def radar_type(self):
        self.current_radar_type = self.comboBox_radar_type.currentText()
        targetstatus.dongtai_biaoding(self.can_num, "radar")

    def online_biaoding(self):
        targetstatus.dongtai_biaoding(self.can_num, "online")

    def keep_online(self):
        self.online_biaoding()
        keep = Timer(0.5, self.keep_online)
        keep.start()
        if not self.progress_ask_flag:
            keep.cancel()

    def ask_progress(self):
        targetstatus.dongtai_biaoding(self.can_num, "progress")
        pro = Timer(0.1, self.ask_progress)
        pro.start()
        if not self.progress_ask_flag:
            pro.cancel()

    def ask_result(self):
        targetstatus.dongtai_biaoding(self.can_num, "result")
        reslut = Timer(0.2, self.ask_result)
        reslut.start()
        if not self.progress_ask_flag:
            reslut.cancel()

    def get_biaoding_value(self):
        targetstatus.dongtai_biaoding(self.can_num, "value")
        self.read_current_value = 2
        biaoding_value = Timer(2, self.change_flag, ("read_value", ))
        biaoding_value.start()

    """
    Flash指令
    """
    def read_flash(self):
        self.label_read_state.setText("开始读取数据...")
        self.flash_flag = "read_flash"
        self.flash_frame_nums = 0
        targetstatus.flash(self.can_num, "kuozhan")
        flash_value = Timer(2, self.change_flag, ("flash_read",))
        flash_value.start()
        bin_folder = os.path.join(os.path.abspath('.'), 'bin文件')
        if not os.path.exists(bin_folder):
            os.mkdir(bin_folder)
        self.bin_file_name = os.path.join(bin_folder, "Flash_" + datetime.datetime.now().strftime('%H%M%S') + ".bin")

    def delete_flash_area(self):
        self.flash_flag = "delete_flash"
        self.label_delete_state.setText("正在擦除Flash区域数据！")
        targetstatus.flash(self.can_num, "kuozhan")
        flash_value = Timer(2, self.change_flag, ("flash_delete",))
        flash_value.start()


    def dongtai_ui(self, analyse_frame):
        for frame in analyse_frame:
            if frame[2] == "0X7EA":
                frame_data = frame[3].split(" ")
                if self.progress_ask_flag and frame_data[1] == '50' and frame_data[2] == '03':
                    self.keep_online()
                    targetstatus.dongtai_biaoding(self.can_num, "run")
                elif self.flash_flag == "read_flash" and frame_data[1] == '50' and frame_data[2] == '03':
                    self.keep_online()
                    targetstatus.flash(self.can_num, "request")
                elif self.flash_flag == "delete_flash" and frame_data[1] == '50' and frame_data[2] == '03':
                    self.keep_online()
                    targetstatus.flash(self.can_num, "delete")
                elif self.flash_flag == "delete_flash" and frame_data[0] == '04'and frame_data[1] == '71' and frame_data[2] == '01':
                    self.label_delete_state.setText("擦除Flash区域数据成功！")
                elif frame_data[1] == '62' and frame_data[2] == "03" and frame_data[3] == "08":
                    if frame_data[4] == "00":
                        self.label_history.setText("未做过动态标定")
                    if frame_data[4] == "01":
                        self.label_history.setText("已做过动态标定")
                elif frame_data[1] == "71" and frame_data[2] == "01":
                    self.ask_progress()
                    self.ask_result()

                elif frame_data[1] == "71" and frame_data[2] == "03":
                    value = int(frame_data[5], 16)
                    if self.progress_ask_flag:
                        self.progressBar.setValue(value)
                    if value == 100:
                        self.progress_ask_flag = False
                        self.get_biaoding_value()

                elif frame_data[1] == "62" and frame_data[2] == "03" and frame_data[3] == "06":
                    if frame_data[4] == "04":
                        self.label_biaoding_info.setText('正在标定（无效）')
                    elif frame_data[4] == "03":
                        self.label_biaoding_info.setText('正在标定（有效）')
                    elif frame_data[4] == "02":
                        self.label_biaoding_info.setText('正在标定')
                    elif frame_data[4] == "01":
                        self.label_biaoding_info.setText('标定成功')
                    elif frame_data[4] == "00":
                        self.label_biaoding_info.setText('标定失败')

                elif frame_data[1] == "62" and frame_data[2] == "03" and frame_data[3] == "07":
                    if self.current_radar_type == '角雷达':
                        biaoding_value = int(frame_data[4] + frame_data[5], 16)*0.01
                    else:
                        biaoding_value = int(frame_data[4] + frame_data[5], 16) * 0.01-15
                    if self.read_current_value == 1:
                        self.label_current_value.setText('标定结果:'+str(biaoding_value))
                    if self.read_current_value == 2:
                        self.label_biaoding_value.setText('标定结果:' + str(biaoding_value))
                else:
                    pass
            if frame[2] == "0X7EE":
                self.flash_frame_nums = self.flash_frame_nums +1
                frame_data = frame[3].split(" ")
                frame_str = ''.join(frame_data)[:8]
                frame_bytes = int(frame_str, 16).to_bytes(4,'big')
                with open(self.bin_file_name, "ab+") as binfile:
                    binfile.write(frame_bytes)
                if self.flash_frame_nums >= 1153:
                    self.label_read_state.setText("读取完成， bin文件已经生成！")
                else:
                    self.label_read_state.setText("正在读取Flash数据！")
    def get_current_can(self):
        my_current_can = self.canSelectcomboBox.currentText()

        if self.thread_list:
            for thr in self.thread_list:
                thr.terminate()
                thr.wait(1)
            self.thread_list = []
        if my_current_can == "CAN1":
            self.can_num = 0
            # ax, fig = self.draw_targets()

            self.Can1Variable, self.Can2Variable, self.ta1, self.ta2 = self.start_can(self.can_num)
            gv.set_variable("Can1Variable", self.Can1Variable)
            gv.set_variable("Can2Variable", self.Can2Variable)
            gv.set_variable('ta1', self.ta1)
            gv.set_variable('ta2', self.ta2)
            self.thread_list.append(self.ta1)
            # # self.cantext.draw.connect(self.refresh_targets)
            # self.refresh = Refresh(ax, fig)
            # self.refresh.start()
        if my_current_can == "CAN2":
            self.can_num = 1
            # ax, fig = self.draw_targets()

            self.Can1Variable, self.Can2Variable, self.ta1, self.ta2 = self.start_can(self.can_num)
            gv.set_variable("Can1Variable", self.Can1Variable)
            gv.set_variable("Can2Variable", self.Can2Variable)
            gv.set_variable('ta1', self.ta1)
            gv.set_variable('ta2', self.ta2)

            # # self.cantext.draw.connect(self.refresh_targets)
            # self.refresh = Refresh(ax, fig)
            # self.refresh.start()
            self.thread_list.append(self.ta2)



    def start_can(self, can_num):
        Can1Variable = definevariable()
        Can2Variable = definevariable()

        ta1 = CanThrerad(0, Can1Variable)
        ta2 = CanThrerad(1, Can2Variable)
        if can_num == 0:
            ta1.text.connect(self.printcan)
            ta1.analyse_frame.connect(self.dongtai_ui)
            ta1.start()
        if can_num == 1:
            ta2.text.connect(self.printcan)
            ta2.analyse_frame.connect(self.dongtai_ui)
            ta2.start()
        return Can1Variable, Can2Variable, ta1, ta2

    def draw_targets(self):

        # rho = np.arange(0, 2.5, 0.02)  # 极径，0--2.5,间隔0.02
        # theta = 2 * np.pi * rho  # 角度，单位：弧度
        # self.ui.widgetPolar.figure.clear()
        # ##ax1是matplotlib.projections.polar.PolarAxes类型的子图
        # ax1 = self.ui.widgetPolar.figure.add_subplot(1, 1, 1, polar=True)
        # ax1.plot(theta, rho, "r", linewidth=3)
        # ax1.set_rmax(3)  # 极径最大值
        # ax1.set_rticks([0, 1, 2])  # 极径刻度坐标
        # ax1.set_rlabel_position(90)  # 极径刻度坐标，90°是正北
        # ax1.grid(self.ui.chkBoxPolar_gridOn.isChecked())  # 是否显示网格


        self.widgetHist.figure.clear()
        self.ax = self.widgetHist.figure.add_subplot(1, 1, 1, polar=True)

        # self.ax.set_thetagrids(np.arange(-60, 61, 10.0))
        # self.ax.set_theta_zero_location('N')
        # self.ax.set_theta_direction(1)
        # self.ax.set_thetamin(-60)  # 设置极坐标图开始角度为0°
        # self.ax.set_thetamax(60)  # 设置极坐标结束角度为180°
        # self.ax.set_rgrids(np.arange(0, 61.0, 20.0))
        # self.ax.set_rlim(0.0, 60.0)  # 标签范围为[0, 100)
        # self.ax.set_yticklabels(['0', '20', '40', '60'])
        # self.ax.grid(True, linestyle="-", color="k", linewidth=0.5, alpha=0.5)
        # self.ax.set_axisbelow('False')  # 使散点覆盖在坐标系之上
        # self.ax.set_rlabel_position(0)  # 标签显示在0°
        # # self.ax.plot([5.497, 0, 0.785], [50, 70, 50])
        # self.ax.scatter([5.497, 0, 0.785], [50, 70, 50], s=5.0)
        return self.ax, self.widgetHist.figure

    def printcan(self, can_list):
        for frame in can_list:
            self.textBrowser_cantext.append(f'{frame[0]}  {frame[1]}  {frame[2]} {frame[3]}')
        # self.textBrowser_cantext.moveCursor(self.textBrowser_cantext.textCursor().End)
        # self.textBrowser_cantext.append(f"{hex(canobject[0])}, {canobject[1]}")
        # print(hex(canobject[0]), canobject[1])


    def SysCalibrationFunction(self):
        self.SysCaliResult.setText(None)
        self.AngleResult.setText(None)
        self.SteplineEdit.setText(None)
        # 为1表示做了系统标定
        self.sysCaliOrNot = 1

        # 这里就是获取值
        # 批次
        # SN号
        # 客户编码
        self.confirmWindow = ConfirmWindow(self.doubleCanVariable, SysCaliResult=self.SysCaliResult, can = self.can_num)
        self.confirmWindow.show_text()
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

    def update(self):
        targetShowValueNew = self.targetShowValue.getAllValue()

        TargetStatusMessageNew = self.CanVariable.getTargetStatusMessage()
        if TargetStatusMessageNew != self.TargetStatusMessageOld:
            self.TargetStatusMessageOld = TargetStatusMessageNew
            statusdisplay.TargetStatusDisplay(TargetStatusMessageNew, self.statuslineEdit)
            self.CanVariable.clearTargetStatusMessage()
        if targetShowValueNew != self.targetShowValueOld:
            self.targetShowValueOld = targetShowValueNew
            targetShowValueOldList = list(self.targetShowValueOld)
            distLong = targetShowValueOldList[2]
            distLat = targetShowValueOldList[3]
            # print("distLong {}".format(distLong))
            # print("distLat {}".format(distLat))
            #显示旧值
            if distLong != [] and distLat != []:
                if self.firstTimeDisplay == 1:
                    self.p.removeItem(self.clusterValue)
                    self.clusterValue = pg.ScatterPlotItem(x=distLat, y=distLong, brush='ff0000', size=5)
                    self.p.addItem(self.clusterValue)
                else:
                    self.clusterValue = pg.ScatterPlotItem(x=distLat, y=distLong, brush='ff0000', size=5)
                    self.p.addItem(self.clusterValue)
                    self.firstTimeDisplay = 1

    def TargetStatusFunction(self):
        # 做了系统标定或者角度标定
        self.canSelectTargetStatus = self.canSelectcomboBox.currentText()
        if self.canSelectTargetStatus == "CAN1":
            canChannelSelect = 1
            self.CanVariable = gv.get_variable("Can1Variable")
        else:
            canChannelSelect = 2
            self.CanVariable = gv.get_variable("Can2Variable")
            # 没有做系统标定和角度标定
        if self.systemcalicheckBox.checkState() == Qt.Checked:
            sysCaliTargetStatus = 1
        elif self.systemcalicheckBox.checkState() == Qt.Unchecked:
            sysCaliTargetStatus = 0
        if self.anglecalicheckBox.checkState() == Qt.Checked:
            angleCaliTargetStatus = 1
        elif self.anglecalicheckBox.checkState() == Qt.Unchecked:
            angleCaliTargetStatus = 0
        targetstatus.TargetStatus(canChannelSelect, sysCaliTargetStatus, angleCaliTargetStatus, self.doubleCanVariable,
                                  self.operationThreadVariables, self.targetShowValue)
        #处理 Target Status 显示
        gv.set_variable('status_flag', True)

        if self.timer == 0:
            self.timer = QtCore.QTimer()
            # 定时调用的函数不需要加括号()
            self.timer.timeout.connect(self.update)
            # start()时间为ms
            self.timer.start(5)

if __name__ == "__main__":
    app = QApplication(argv)
    window = MyApp()
    window.show()
    exit(app.exec_())



