import warnings
warnings.filterwarnings("ignore")
import datetime
import time
import pyqtgraph as pg
from pyqtgraph.Point import Point
from pyqtgraph.Qt import QtGui
from threading import Timer
import global_variable as gv
gv._init()
gv.set_variable('status_flag', False)
from calibration.definevariable import definevariable
from PyQt5.QtCore import QThread, pyqtSignal, QDir, Qt,QItemSelectionModel
from PyQt5 import QtCore, QtWidgets
from ctypes import *
import ctypes
import inspect
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QFileDialog, QTableWidgetItem
from sys import argv, exit
import os
from calibration.multhread import operationthread
import numpy as np
np.set_printoptions(precision=2)
from calibrationWindow import Ui_biaoding
from warning import Ui_warning
from confirm import Ui_Confirm
from StatusShow import statusdisplay

from calibration import snvalue

from calibration.definevariable import canvariable
from calibration.caliresultshow import MainWindowThread


from StatusShow import targetstatus

#存储处理数据的线程
from calibration.definevariable import operationthreadvariables

from calibration.definevariable import targetshowvalue
from PyQt5.QtGui import QStandardItemModel, QStandardItem
VCI_USBCAN2 = 4
STATUS_OK = 1

ListValueID = []
CanDLLName = './ControlCAN.dll' #把DLL放到对应的目录下
canDLL = windll.LoadLibrary('./ControlCAN.dll')
gv.set_variable('dll', canDLL)




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

def  write_test_flow(Can1Variable, Can2Variable, SysCaliResult, excelSnNameVal, can_num):
    if Can1Variable and can_num==0:
        Can1Variable.changeOperationStatus(1)
        opCan1 = operationthread(CaliResult=SysCaliResult, CanVariable=Can1Variable, ExcelName=excelSnNameVal, channel=0)  # 实例化线程
        opCan1.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opCan1.start()  # 开启ta线程
    if Can2Variable and can_num==1:
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
    def __init__(self, channel, CanVariable, Acc_Code, Mask_Code):
        super().__init__()
        # self.cluster_list = [[],[],[]]
        self.target_scatter = []
        self.object_scatter = []
        self.current_all_scatter = []
        self.current_all_object = []

        self.channel = channel
        self.CanVariable = CanVariable
        self.ta1 = 0
        self.ta2 = 0
        self.frame_num = 2000
        self.Acc_Code = Acc_Code
        self.Mask_Code = Mask_Code
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
        for i in range(self.frame_num):
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
        vci_initconfig = VCI_INIT_CONFIG(self.Acc_Code, self.Mask_Code, 0, 2, 0x00, 0x1C, 0)
        # vci_initconfig = VCI_INIT_CONFIG(0xe1800000, 0x1e800000, 0, 2, 0x00, 0x1C, 0)

        ret = canDLL.VCI_InitCAN(VCI_USBCAN2A, 0, self.channel, byref(vci_initconfig))
        if ret != STATUS_OK:
            print('调用 VCI_InitCAN出错\r\n')
            return

        ret = canDLL.VCI_StartCAN(VCI_USBCAN2A, 0, self.channel)
        if ret != STATUS_OK:
            print('调用 VCI_StartCAN出错\r\n')
            return


        ubyte_array = c_ubyte * 8
        ubyte_3array = c_ubyte * 3
        a = ubyte_array(0, 0, 0, 0, 0, 0, 0, 0)
        b = ubyte_3array(0, 0, 0)
        name = "can_log_"+time.strftime('%H%M%S')+".csv"
        gv.set_variable('can_log', name)
        while True:
            analyse_flag = False
            vci_can_obj = VCI_CAN_OBJ(*(0x0, 0, 0, 1, 0, 0, 8, a, b) * self.frame_num)
            ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, self.channel, byref(vci_can_obj), self.frame_num, 0)    #每次接收一帧数据，这里设为1

            if ret > 0:
                time_now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                frame = []
                if gv.get_variable("can_data_to_radar") != "":
                    frame.extend(gv.get_variable("can_data_to_radar"))
                    gv.set_variable("can_data_to_radar", "")
                for i in range(self.frame_num):
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
                            self.CanVariable.setTargetStatusMessage(list(data))
                            bin_can_frame_list = [bin(x)[2:].zfill(8) for x in data]
                            bin_can_frame_str = ''.join(bin_can_frame_list)
                            ID = int(bin_can_frame_str[0:8], 2)
                            DistLong = int(bin_can_frame_str[8:18], 2) * 0.2 - 102
                            DistLat = int(bin_can_frame_str[18:28], 2) * 0.2 - 102
                            VrelLong = int(bin_can_frame_str[28:38], 2) * 0.25 - 128
                            VrelLat = int(bin_can_frame_str[38:47], 2) * 0.25 - 64
                            Status = (int(bin_can_frame_str[50:53], 2))
                            PossibilitofExist = (int(bin_can_frame_str[53:56], 2))
                            RCS = int(bin_can_frame_str[56:64], 2) * 0.5 - 64
                            # theta = math.atan2(DistLat, DistLong)
                            # r = math.sqrt(DistLong * DistLong + DistLat * DistLat)
                            self.target_scatter.extend([[DistLat, DistLong]])
                            self.current_all_scatter.extend([[ID, DistLong, DistLat, VrelLong, VrelLat, Status, PossibilitofExist, RCS]])
                        if id == 0x70A:
                            if not gv.get_variable("stop_scatter"):
                                # gv.set_variable('target', self.cluster_list)
                                gv.set_variable('target_scatter', np.array(self.target_scatter))
                                gv.set_variable('target_scatter_info',  np.array(self.current_all_scatter))
                            # self.cluster_list = [[], []]
                            self.target_scatter.clear()
                            self.current_all_scatter.clear()
                        if id == 0x60B:
                            bin_can_frame_list = [bin(x)[2:].zfill(8) for x in data]
                            bin_can_frame_str = ''.join(bin_can_frame_list)
                            ID = int(bin_can_frame_str[0:8], 2)
                            DistLong = int(bin_can_frame_str[8:18], 2) * 0.2 - 102
                            DistLat = int(bin_can_frame_str[18:28], 2) * 0.2 - 102
                            VrelLong = int(bin_can_frame_str[28:38], 2) * 0.25 - 128
                            VrelLat = int(bin_can_frame_str[38:47], 2) * 0.25 - 64
                            Status = (int(bin_can_frame_str[50:53], 2))
                            PossibilitofExist = (int(bin_can_frame_str[53:56], 2))
                            RCS = int(bin_can_frame_str[56:64], 2) * 0.5 - 64
                            if ID != 255:
                                self.object_scatter.extend([[DistLat, DistLong]])
                                self.current_all_object.extend([[ID, DistLong, DistLat, VrelLong, VrelLat, Status, PossibilitofExist, RCS]])
                        if id == 0x60A:
                            if not gv.get_variable("stop_scatter"):
                                gv.set_variable('object_scatter', np.array(self.object_scatter))
                                gv.set_variable('object_scatter_info', np.array(self.current_all_object))
                            self.object_scatter.clear()
                            self.current_all_object.clear()
                        if id == 0x7EA or id == 0x7EE:
                            analyse_flag = True
                    else:
                        break

                self.text.emit(frame)
                if analyse_flag:
                    self.analyse_frame.emit(frame)

            time.sleep(0.020)
class Graph(pg.GraphItem):
    click_trigger = pyqtSignal(object)
    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        self.textItems = []
        pg.GraphItem.__init__(self)
        self.scatter.sigClicked.connect(self.clicked)
    def setData(self, **kwds):
        self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        self.setTexts(self.text)
        self.updateGraph()

    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)

    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        for i, item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():

            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def clicked(self, pts):
        current_index = pts.ptsClicked[0].index()
        if pts.ptsClicked[0].size() == 5:
            self.click_trigger.emit(gv.get_variable('target_scatter_info')[current_index])
        else:
            self.click_trigger.emit(gv.get_variable('object_scatter_info')[current_index])
class MyGraphView(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.my_current_pts = None

    def mouseMoveEvent(self, ev):
        gv.set_variable('stop_scatter', True)
        if self.lastMousePos is None:
            self.lastMousePos = Point(ev.pos())
        delta = Point(ev.pos() - QtCore.QPoint(*self.lastMousePos))
        self.lastMousePos = Point(ev.pos())

        QtGui.QGraphicsView.mouseMoveEvent(self, ev)
        if not self.mouseEnabled:
            return
        self.sigSceneMouseMoved.emit(self.mapToScene(ev.pos()))

        if self.clickAccepted:  ## Ignore event if an item in the scene has already claimed it.
            return

        if ev.buttons() == QtCore.Qt.RightButton:
            delta = Point(np.clip(delta[0], -50, 50), np.clip(-delta[1], -50, 50))
            scale = 1.01 ** delta
            self.scale(scale[0], scale[1], center=self.mapToScene(self.mousePressPos))
            self.sigDeviceRangeChanged.emit(self, self.range)

        elif ev.buttons() in [QtCore.Qt.MidButton, QtCore.Qt.LeftButton]:  ## Allow panning by left or mid button.
            px = self.pixelSize()
            tr = -delta * px

            self.translate(tr[0], tr[1])
            self.sigDeviceRangeChanged.emit(self, self.range)
    def leaveEvent(self, ev):
        gv.set_variable('stop_scatter', False)
        return


class MyApp(Ui_biaoding,QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        gv.set_variable('target', [])
        self.channel1 = 0
        self.channel2 = 0
        self.FilePath = 0
        self.ta1 = 0
        self.ta2 = 0
        self.Can1Variable = None
        self.Can2Variable = None
        self.CanVariable = None
        self.doubleCanVariable = canvariable()

        # 存储处理数据的线程
        self.timer = 0
        self.operationThreadVariables = operationthreadvariables()
        self.targetShowValue = targetshowvalue()
        self.ui_connection()
        self.init_dongtai()
        self.init_scatter()
        self.init_table()
        gv.set_variable("enter_table_view", False)

    def ui_connection(self):
        self.SysCaliStart.clicked.connect(self.SysCalibrationFunction)
        self.statuspushButton.clicked.connect(self.TargetStatusFunction)
        self.comboBox_radar_type.currentTextChanged.connect(self.radar_type)
        self.pushButton_biaoding_history.clicked.connect(self.read_history)
        self.pushButton_start_biaoding.clicked.connect(self.run_biaoding)
        self.pushButton_read_biaoding_value.clicked.connect(self.read_value)
        self.pushButton_flash.clicked.connect(self.read_flash)
        self.pushButton_delete.clicked.connect(self.delete_flash_area)
        self.groupBox_5.setDisabled(True)
        self.pushButton_printcan.clicked.connect(self.set_print_can_flag)
    def init_dongtai(self):

        #保存旧值
        self.enter_kuozhan_result = False
        self.TargetStatusMessageOld = []
        self.can_num = 0
        self.thread_list = []
        self.pushButton_startcan.clicked.connect(self.get_current_can)
        self.pushButton_stopcan.clicked.connect(self.stop_can)
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
        self.get_filename_path = ""

    def init_scatter(self):
        # 点迹显示
        gv.set_variable("target_scatter", [])
        gv.set_variable("stop_scatter", False)
        gv.set_variable('object_scatter', np.array([]))
        gv.set_variable('target_scatter', np.array([]))
        gv.set_variable('target_scatter_info', np.array([]))
        gv.set_variable('object_scatter_info', np.array([]))

        self.can_isRun = False
        self.first_time_flag = True
        self.generate_image()
        self.my_scatter = Graph()
        self.my_scatter.click_trigger.connect(self.write_2_table_content)
        self.my_object = Graph()
        self.my_object.click_trigger.connect(self.write_2_table_content)
        self.plot.addItem(self.my_scatter)
        self.plot.addItem(self.my_object)
        self.scatter_timer = QtCore.QTimer()
        self.scatter_timer.setInterval(5)
        self.scatter_timer.timeout.connect(self.update_scatter)
        self.scatter_timer.start()
        gv.set_variable('scatter_timer', self.scatter_timer)
        self.pushButton_stopcan.setEnabled(False)

    def init_table(self):
        gv.set_variable("stop_print_can", False)
        # self.page_3.enterEvent = self.enterEvent
        # self.page_3.leaveEvent = self.leaveEvent
        self.__ColCount = 4  # 列数=6
        self.itemModel = QStandardItemModel(0, self.__ColCount, self)  # 数据模型,10行6列
        self.selectionModel = QItemSelectionModel(self.itemModel)  # Item选择模型
        self.tableView.setModel(self.itemModel) #设置数据模型
        self.tableView.setSelectionModel(self.selectionModel)    #设置选择模型
        self.tableView.setAlternatingRowColors(True)  # 交替行颜色
        headerText = ["时间", "传输方向", "帧ID", "数据"]
        self.itemModel.setHorizontalHeaderLabels(headerText)
        self.lineEdit_rowNum.textChanged.connect(self.rowNumChanged)
        try:
            self.rowNum = int(self.lineEdit_rowNum.text())
        except ValueError:
            self.lineEdit_rowNum.setText("重新输入！")
        self.scatter_type = "Target and Object"
        self.comboBox_tatr.currentTextChanged.connect(self.output_scatter_type)

    def enterEvent(self, event):
        gv.set_variable("enter_table_view", True)
    def leaveEvent(self, event):
        gv.set_variable("enter_table_view", False)

    def output_scatter_type(self):
        self.scatter_type = self.comboBox_tatr.currentText()
        if self.scatter_type == "Object":
            self.plot.removeItem(self.my_scatter)
            self.plot.addItem(self.my_object)
        elif self.scatter_type == "Target":
            self.plot.removeItem(self.my_object)
            self.plot.addItem(self.my_scatter)
        else:
            self.plot.addItem(self.my_scatter)
            self.plot.addItem(self.my_object)
    def rowNumChanged(self):
        try:
            self.rowNum = int(self.lineEdit_rowNum.text())
        except ValueError:
            self.lineEdit_rowNum.setText("重新输入！")

    def generate_image(self):
        verticalLayout = QVBoxLayout(self.graphicsView)
        #k是black缩写，防止与blue重复
        pg.setConfigOption('background', 0.8)
        pg.setConfigOption('foreground', 'k')
        win = MyGraphView(self.graphicsView)
        self.widget = verticalLayout.addWidget(win)
        self.plot = win.addPlot()
        # alpha为网格的不透明度
        self.plot.showGrid(x=True, y=True)
        self.plot.setXRange(-60, 60)
        self.plot.setYRange(0, 100)

    def write_2_table_content(self, content):
        for index, item in enumerate(content):
            item = QTableWidgetItem(str(round(float(item), 2)), 1000)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(0, index, item)


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
        kuozhan_check = Timer(1, self.enter_kuozhan)
        kuozhan_check.start()

    def enter_kuozhan(self):
        if not self.enter_kuozhan_result:
            self.label_kuozhan.setText("进入扩展模式失败，请重新再试！")
        else:
            self.label_kuozhan.setText("成功进入扩展模式！")
        self.enter_kuozhan_result = False

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
                    self.enter_kuozhan_result = True
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
        self.can_isRun = True
        my_current_can = self.canSelectcomboBox.currentText()
        sid = self.lineEdit_slvboID.text()
        eid = self.lineEdit_elvboID.text()
        Acc_Code = 0x80000008
        Mask_Code = 0xFFFFFFFF
        if self.checkBox_slvbo.checkState():
            try:
                start_id_int = int(sid, 16)
                end_id_int = int(eid, 16)
            except ValueError:
                self.lineEdit_slvboID.setText("重新输入！")
                self.lineEdit_elvboID.setText("重新输入！")
                return
            My_Sid = start_id_int << 21
            Acc_Code = end_id_int << 21
            Mask_Code = My_Sid ^ Acc_Code
        if self.thread_list:
            for thr in self.thread_list:
                thr.terminate()
                thr.wait(1)
            self.thread_list = []
        if my_current_can == "CAN1":
            self.can_num = 0

            self.Can1Variable, self.Can2Variable, self.ta1, self.ta2 = self.start_can(self.can_num, Acc_Code, Mask_Code)
            gv.set_variable("Can1Variable", self.Can1Variable)
            gv.set_variable("Can2Variable", self.Can2Variable)
            gv.set_variable('ta1', self.ta1)
            gv.set_variable('ta2', self.ta2)
            self.thread_list.append(self.ta1)
        if my_current_can == "CAN2":
            self.can_num = 1

            self.Can1Variable, self.Can2Variable, self.ta1, self.ta2 = self.start_can(self.can_num, Acc_Code, Mask_Code)
            gv.set_variable("Can1Variable", self.Can1Variable)
            gv.set_variable("Can2Variable", self.Can2Variable)
            gv.set_variable('ta1', self.ta1)
            gv.set_variable('ta2', self.ta2)
            self.thread_list.append(self.ta2)

    def stop_can(self):
        self.can_isRun = False
        self.pushButton_startcan.setEnabled(True)
        self.pushButton_stopcan.setEnabled(False)
        if gv.get_variable('dll'):
            dll = gv.get_variable('dll')
            dll.VCI_CloseDevice(4, 0)

    def start_can(self, can_num, Acc_Code, Mask_Code):
        self.pushButton_stopcan.setEnabled(True)
        self.pushButton_startcan.setEnabled(False)
        Can1Variable = definevariable()
        Can2Variable = definevariable()

        ta1 = CanThrerad(0, Can1Variable, Acc_Code, Mask_Code)
        ta2 = CanThrerad(1, Can2Variable, Acc_Code, Mask_Code)
        if can_num == 0:
            ta1.text.connect(self.printcan)
            ta1.analyse_frame.connect(self.dongtai_ui)
            ta1.start()
        if can_num == 1:
            ta2.text.connect(self.printcan)
            ta2.analyse_frame.connect(self.dongtai_ui)
            ta2.start()
        return Can1Variable, Can2Variable, ta1, ta2

    def set_print_can_flag(self):
        if self.pushButton_printcan.text() == "暂停报文滚动":
            self.pushButton_printcan.setText("动态显示报文")
            gv.set_variable("stop_print_can", True)
        else:
            self.pushButton_printcan.setText("暂停报文滚动")
            gv.set_variable("stop_print_can", False)
    def printcan(self, can_list):
        if gv.get_variable("stop_print_can"):
            return
        for frame in can_list:
            itemlist = [QStandardItem(frame[0]),  QStandardItem(frame[1]), QStandardItem(frame[2]),  QStandardItem(frame[3])]
            if frame[1] == "to radar  ":
                for item in itemlist:
                    item.setBackground(QtGui.QBrush(Qt.yellow))
            if frame[2] == "0X7EA":
                for item in itemlist:
                    item.setBackground(QtGui.QBrush(Qt.green))
            self.itemModel.appendRow(itemlist)
            if self.itemModel.rowCount() > self.rowNum:
                count = self.itemModel.rowCount() - self.rowNum
                self.itemModel.removeRows(0, count)
        # scroll_flag = gv.get_variable("enter_table_view")
        # if not scroll_flag:
        #     self.tableView.scrollToBottom()
        self.tableView.scrollToBottom()

    def SysCalibrationFunction(self):
        self.SysCaliResult.setText(None)
        self.AngleResult.setText(None)
        self.SteplineEdit.setText(None)
        # 为1表示做了系统标定


        self.get_filename_path, ok = QFileDialog.getOpenFileName(self, "选取单个文件", QDir.currentPath(), "All Files (*);;Text Files (*.xls)")
        if not ok:
            return
        gv.set_variable("biaoding_wenjian", self.get_filename_path)
        self.enter_test_mode()


    def enter_test_mode(self):
        excelSnNameVal = snvalue.create_excel_sn()
        Can1Variable, Can2Variable, ta1, ta2 = start_can_test(self.SysCaliResult, excelSnNameVal, self.can_num)
        self.doubleCanVariable.changeCanVariable(Can1Variable, Can2Variable, ta1, ta2, excelSnNameVal)
        #主窗口的“确认”按钮后面显示“正在测试”/“完成”
        opMainWindow = MainWindowThread(Can1Variable, Can2Variable, self.SysCaliResult, ta1=ta1, ta2=ta2, can_num=self.can_num)
        opMainWindow.daemon = False  # 当 daemon = False 时，线程不会随主线程退出而退出（默认时，就是 daemon = False）
        opMainWindow.start()  # 开启ta线程

    def update_scatter(self):
        if self.can_isRun:
            if self.scatter_type == "Target and Object":
                scatter = gv.get_variable("target_scatter")
                if len(scatter) > 0 and not gv.get_variable("stop_scatter"):
                    self.my_scatter.setData(pos=scatter,  size=5,  brush='ff0000')
                scatter = gv.get_variable("object_scatter")
                if len(scatter) > 0 and not gv.get_variable("stop_scatter"):
                    self.plot.addItem(self.my_object)
                    self.my_object.setData(pos=scatter,  size=10,  brush='00ff00')
                else:
                    self.plot.removeItem(self.my_object)
            elif self.scatter_type == "Object":
                scatter = gv.get_variable("object_scatter")
                if len(scatter) > 0 and not gv.get_variable("stop_scatter"):
                    self.plot.addItem(self.my_object)
                    self.my_object.setData(pos=scatter,  size=10,  brush='00ff00')
                else:
                    self.plot.removeItem(self.my_object)
            elif self.scatter_type == "Target":
                scatter = gv.get_variable("target_scatter")
                if len(scatter) > 0 and not gv.get_variable("stop_scatter"):
                    self.my_scatter.setData(pos=scatter,  size=5,  brush='ff0000')

    def update(self):

        TargetStatusMessageNew = self.CanVariable.getTargetStatusMessage()
        if TargetStatusMessageNew != self.TargetStatusMessageOld:
            self.TargetStatusMessageOld = TargetStatusMessageNew
            statusdisplay.TargetStatusDisplay(TargetStatusMessageNew, self.statuslineEdit)
            self.CanVariable.clearTargetStatusMessage()



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



