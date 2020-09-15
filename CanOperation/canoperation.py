from ctypes import *
from calibration.definevariable import definevariable
from calibration.multhread import mythread
import os
VCI_USBCAN2 = 4
STATUS_OK = 1

CanDLLName = os.path.join(os.getcwd(), 'ControlCAN.dll') #把DLL放到对应的目录下
canDLL = windll.LoadLibrary(CanDLLName)

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

def can_open(groupCan1Info, groupCan2Info):
    Can1Variable = 0
    Can2Variable = 0
    ta1 = 0
    ta2 = 0

    ret = canDLL.VCI_OpenDevice(VCI_USBCAN2, 0, 0)
    # if ret == STATUS_OK:
    #     print('调用 VCI_OpenDevice成功\r\n')
    # if ret != STATUS_OK:
    #     print('调用 VCI_OpenDevice出错\r\n')

    # 初始通道
    vci_initconfig = VCI_INIT_CONFIG(0x80000008, 0xFFFFFFFF, 0,
                                     0, 0x01, 0x1C, 0)  # 波特率250k，正常模式
    if groupCan1Info != "无":
        ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_initconfig))
        # if ret == STATUS_OK:
        #     print('调用 VCI_InitCAN1成功\r\n')
        # if ret != STATUS_OK:
        #     print('调用 VCI_InitCAN1出错\r\n')

        ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
        # if ret == STATUS_OK:
        #     print('调用 VCI_StartCAN1成功\r\n')
        # if ret != STATUS_OK:
        #     print('调用 VCI_StartCAN1出错\r\n')

        Can1Variable = definevariable()
        ta1 = mythread(0, Can1Variable)  # 实例化线程
        ta1.start()  # 开启ta线程

    if groupCan2Info != "无":
        ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 1, byref(vci_initconfig))
        # if ret == STATUS_OK:
        #     print('调用 VCI_InitCAN2成功\r\n')
        # if ret != STATUS_OK:
        #     print('调用 VCI_InitCAN2出错\r\n')

        ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 1)
        # if ret == STATUS_OK:
        #     print('调用 VCI_StartCAN2成功\r\n')
        # if ret != STATUS_OK:
        #     print('调用 VCI_StartCAN2出错\r\n')

        Can2Variable = definevariable()
        ta2 = mythread(1, Can2Variable)  # 实例化线程
        ta2.start()  # 开启ta线程

    return Can1Variable, Can2Variable, ta1, ta2

def can_close():
    ret = canDLL.VCI_CloseDevice(VCI_USBCAN2, 0)
    # if ret == STATUS_OK:
    #     print('调用 VCI_CloseDevice成功\r\n')
    # if ret != STATUS_OK:
    #     print('调用 VCI_CloseDevice出错\r\n')






















