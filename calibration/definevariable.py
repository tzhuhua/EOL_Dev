'''
OperationStatus 为1：系统标定 2：角度标定 3：RCS 4：包络标定
'''
class definevariable:
    def __init__(self):
        self.ListValueMessage = []
        self.OperationStatus = 0
        #是否超时，超时为1，不超时/默认为0
        self.timeOutVal = 0

    def changeOperationStatus(self, x):
        self.OperationStatus = x

    def getOperationStatus(self):
        return self.OperationStatus

    def appendListValueMessage(self, value):
        self.ListValueMessage.append(value)

    def getListValueMessage(self):
        return self.ListValueMessage

    def clearListValueMessage(self):
        self.ListValueMessage = []

    def changeTimeOutVal(self, x):
        self.timeOutVal = x

    def getTimeOutVal(self):
        return self.timeOutVal

#read和write的变量连接
class canvariable:
    def __init__(self):
        self.Can1Variable = 0
        self.Can2Variable = 0
        self.ta1 = 0
        self.ta2 = 0
        self.excelSnNameVal = 0

    def changeCanVariable(self, can1Variable, can2Variable, ta1, ta2, excelSnNameVal):
        self.Can1Variable = can1Variable
        self.Can2Variable = can2Variable
        self.ta1 = ta1
        self.ta2 = ta2
        self.excelSnNameVal = excelSnNameVal

    def getCanVariable(self):
        return self.Can1Variable, self.Can2Variable, self.ta1, self.ta2, self.excelSnNameVal

# 表明是否按下角度确认按钮
class anglecalibrationpress:
    def __init__(self):
        self.angleCaliPress = 0

    def changeAngleCaliPress(self, val):
        self.angleCaliPress = val

    def getAngleCaliPress(self):
        return self.angleCaliPress

# 当前角度的角度标定是否做完
class anglecalibrationcompletednum:
    def __init__(self):
        self.angleCaliCompletedNum = 0

    def changeAngleCaliCompletedNum(self, val):
        self.angleCaliCompletedNum = val

    def getAngleCaliCompletedNum(self):
        return self.angleCaliCompletedNum


