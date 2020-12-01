'''
OperationStatus 为1：系统标定 2：角度标定 3：RCS 4：包络标定
'''


class definevariable:
    def __init__(self):
        self.ListValueMessage = []
        self.OperationStatus = 0
        #是否超时，超时为1，不超时/默认为0
        self.timeOutVal = 0
        #存放target status 信息
        self.targetStatusMessage = []
        #存放过程 cluster 信息
        self.clusterMessageValue = []
        #存放最终需要处理的 cluster 信息
        self.clusterMessageValueResult = []
        #报文 70A 是否接收完成
        self.message70ACompleted = 0
        self.analyseError = 0
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

    def changeAnalyseError(self, x):
        self.analyseError = x

    def getAnalyseError(self):
        return self.analyseError

    def setTargetStatusMessage(self, value):
        self.targetStatusMessage = value

    def getTargetStatusMessage(self):
        return self.targetStatusMessage

    def clearTargetStatusMessage(self):
        self.targetStatusMessage = []

    def appendClusterMessageValue(self, value):
        self.clusterMessageValue.append(value)

    def getClusterMessageValue(self):
        return self.clusterMessageValue

    def clearClusterMessageValue(self):
        self.clusterMessageValue = []

    def copyClusterMessageValueResult(self):
        self.clusterMessageValueResult = self.clusterMessageValue
        # print("self.clusterMessageValue {}".format(self.clusterMessageValue))
        # print("shape1 {}".format(np.array(self.clusterMessageValue).shape[0]))
        # print("shape2 {}".format(np.array(self.clusterMessageValueResult).shape[0]))

    def getClusterMessageValueResult(self):
        return self.clusterMessageValueResult

    def clearClusterMessageValueResult(self):
        self.clusterMessageValueResult = []

    def writeMessage70ACompletedVal(self, value):
        self.message70ACompleted = value

    def getmessage70ACompleted(self):
        return self.message70ACompleted

    def clearMessage70ACompleted(self):
        self.message70ACompleted = 0

#read和write的变量连接
class canvariable:
    def __init__(self):
        self.Can1Variable = 0
        self.Can2Variable = 0
        self.ta1 = 0
        self.ta2 = 0
        self.excelSnNameVal = 0

    def changeCanVariable(self, can1Variable, can2Variable, ta1, ta2, excelSnNameVal=0):
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


class operationthreadvariables:
    def __init__(self):
        self.operationThreadCan1 = 0
        self.operationThreadCan2 = 0

    def changeOperationThreadCan1(self, val):
        self.operationThreadCan1 = val

    def changeOperationThreadCan2(self, val):
        self.operationThreadCan2 = val

    def getOperationThreadCan1(self):
        return self.operationThreadCan1

    def getOperationThreadCan2(self):
        return self.operationThreadCan2

class targetshowvalue:
    def __init__(self):
        self.numOfCluster = []
        self.id = []
        self.distLong = []
        self.distLat = []
        self.vrelLong = []
        self.vrelLat = []
        self.clusterStatus = []
        self.possibilityOfExit = []
        self.rcs = []

    def writeNumOfCluster(self, value):
        self.numOfCluster.append(value)

    def write70bValue(self, idVal, distLongVal, distLatVal, vrelLongVal, vrelLatVal, clusterStatusVal, possibilityOfExitVal, rcsVal):
        self.id.append(idVal)
        self.distLong.append(distLongVal)
        self.distLat.append(distLatVal)
        self.vrelLong.append(vrelLongVal)
        self.vrelLat.append(vrelLatVal)
        self.clusterStatus.append(clusterStatusVal)
        self.possibilityOfExit.append(possibilityOfExitVal)
        self.rcs.append(rcsVal)

    def getAllValue(self):
        return self.numOfCluster, self.id, self.distLong, self.distLat, self.vrelLong, self.vrelLat, self.clusterStatus, self.possibilityOfExit, self.rcs

    def clearAllValue(self):
        self.numOfCluster = []
        self.id = []
        self.distLong = []
        self.distLat = []
        self.vrelLong = []
        self.vrelLat = []
        self.clusterStatus = []
        self.possibilityOfExit = []
        self.rcs = []



