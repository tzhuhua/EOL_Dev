#显示标定的结果
import threading
import ctypes
import inspect
from CanOperation import canoperation

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


#MainWindow显示测试信息
class MainWindowThread(threading.Thread):
    def __init__(self, Can1Variable, Can2Variable, SysCaliResult, ta1=None, ta2=None, can_num=None):
        threading.Thread.__init__(self)
        self.Can1Variable = Can1Variable
        self.Can2Variable = Can2Variable
        self.SysCaliResult = SysCaliResult
        self.ta1 = ta1
        self.ta2 = ta2
        self.can_num = can_num
    def run(self):
        self.SysCaliResult.setText("正在标定")

        if self.can_num == 0:
            while True:
                #为2表示是系统标定完成
                if self.Can1Variable.getOperationStatus() == 2 or self.Can1Variable.getOperationStatus() == 4:
                    #当做完read操作，需要关闭所有线程
                    # if self.Can1Variable.getOperationStatus() == 4:
                    #     canoperation.can_close()
                    #     stop_thread(self.ta1)
                    if self.Can1Variable.getTimeOutVal() == 1:
                        self.SysCaliResult.setText("超时失败！")
                        canoperation.can_close()
                        stop_thread(self.ta1)
                    elif self.Can1Variable.getAnalyseError() != 0:
                        self.SysCaliResult.setText(self.Can1Variable.getAnalyseError())
                        self.Can1Variable.changeAnalyseError(0)
                    else:
                        self.SysCaliResult.setText("标定成功！")
                    self.Can1Variable.changeOperationStatus(0)
                    self.Can1Variable.changeTimeOutVal(0)
                    break
        if self.can_num == 1:
            while True:
                if self.Can2Variable.getOperationStatus() == 2 or self.Can2Variable.getOperationStatus() == 4:
                    # 当做完read操作，需要关闭所有线程
                    # if self.Can2Variable.getOperationStatus() == 4:
                    #     canoperation.can_close()
                    #     stop_thread(self.ta2)
                    if self.Can2Variable.getTimeOutVal() == 1:
                        self.SysCaliResult.setText("超时失败")
                        canoperation.can_close()
                        stop_thread(self.ta2)
                    else:
                        self.SysCaliResult.setText("完成")
                    self.Can2Variable.changeOperationStatus(0)
                    self.Can2Variable.changeTimeOutVal(0)
                    break


