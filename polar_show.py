def StartRealTimeDatAnalysisFunction(self):

    if self.timer == 0:
        self.timer = QtCore.QTimer()
        # 定时调用的函数不需要加括号()
        self.timer.timeout.connect(self.update)
        # start()时间为ms
        self.timer.start(5)

    def update(self):
        global colorBlock
        p = self.win.get_pwin()
        xPositionVal, yPositionVal, targetDicVal = self.targetData.get_data()
        horizontalPositionVal, verticalPositionalVal, objectDicVal = self.objectData.get_data()

        if self.comboBoxCurrVal == 'Target' or self.comboBoxCurrVal == 'Debug':
            if xPositionVal != [] and xPositionVal != 0:
                #不是第一次画图
                if self.oldXPositionVal != 0:
                    if xPositionVal != self.oldXPositionVal:
                        #没有按键按下
                        if self.keyPressVal == 0:
                            self.targetDataOld = self.targetData.get_completed_val()
                            # 获取target num 的值
                            self.targetNum = self.targetData.get_target_num()
                            if self.targetNum > self.maxTargetNum:
                                self.maxTargetNum = self.targetNum
                            self.TargetNumlineEdit.setText(str(self.targetNum))
                            self.MaxNumlineEdit.setText(str(self.maxTargetNum))
                            colorXResult, colorYResult = colordisplay.colordisplayfunction(self.targetDataOld, xPositionVal, yPositionVal)
                            #当在Debug模式的时候，不需要清除object
                            if self.sObject != 0 and self.comboBoxCurrVal == 'Target':
                                p.removeItem(self.sObject)
                            #获取颜色的色块数
                            colorNumVal = np.array(colorXResult).shape[0]
                            if self.sTargetOne != 0:
                                p.removeItem(self.sTargetOne)
                            if self.sTargetTwo != 0:
                                p.removeItem(self.sTargetTwo)
                            if self.sTargetThree != 0:
                                p.removeItem(self.sTargetThree)
                            if self.sTargetFour != 0:
                                p.removeItem(self.sTargetFour)
                            for i in range(colorNumVal):
                                if i == 0:
                                    self.sTargetOne = pg.ScatterPlotItem(x=colorXResult[0], y=colorYResult[0],
                                                                         brush=colorBlock[0], size=5)
                                    p.addItem(self.sTargetOne)
                                elif i == 1:
                                    self.sTargetTwo = pg.ScatterPlotItem(x=colorXResult[1], y=colorYResult[1],
                                                                         brush=colorBlock[1], size=5)
                                    p.addItem(self.sTargetTwo)
                                elif i == 2:
                                    self.sTargetThree = pg.ScatterPlotItem(x=colorXResult[2], y=colorYResult[2],
                                                                         brush=colorBlock[2], size=5)
                                    p.addItem(self.sTargetThree)
                                elif i == 3:
                                    self.sTargetFour = pg.ScatterPlotItem(x=colorXResult[3], y=colorYResult[3],
                                                                           brush=colorBlock[3], size=5)
                                    p.addItem(self.sTargetFour)

                            # 核运行时间
                            self.z71OperationTime, self.z72OperationTime = self.operationTime.get_operation_time()
                            self.z71lineEdit.setText(str(self.z71OperationTime))
                            self.z72lineEdit.setText(str(self.z72OperationTime))

                            self.oldXPositionVal = xPositionVal
                            self.targetDataOld = self.targetData.get_completed_val()
                            self.oldTargetXPositionVal = xPositionVal
                            self.oldTargetYPositionVal = yPositionVal
                            self.numTarget = 0
                        #有按键按下
                        else:
                            self.oldXPositionVal = xPositionVal
                            if self.numTarget == 0:
                                print("oldTargetXPositionVal={}".format(self.oldTargetXPositionVal))
                                print("oldTargetYPositionVal={}".format(self.oldTargetYPositionVal))
                                print("targetDicVal={}".format(self.targetDataOld))
                                self.numTarget = 1
                else:
                    #第一次画图
                    self.targetDataOld = self.targetData.get_completed_val()
                    #获取target num 的值
                    self.targetNum = self.targetData.get_target_num()
                    self.maxTargetNumt = self.targetNum
                    self.TargetNumlineEdit.setText(str(self.targetNum))
                    self.MaxNumlineEdit.setText(str(self.maxTargetNum))

                    colorXResult, colorYResult = colordisplay.colordisplayfunction(self.targetDataOld, xPositionVal,
                                                                                   yPositionVal)
                    if self.sObject != 0 and self.comboBoxCurrVal == 'Target':
                        p.removeItem(self.sObject)
                    # 获取颜色的色块数
                    colorNumVal = np.array(colorXResult).shape[0]
                    if self.sTargetOne != 0:
                        p.removeItem(self.sTargetOne)
                    if self.sTargetTwo != 0:
                        p.removeItem(self.sTargetTwo)
                    if self.sTargetThree != 0:
                        p.removeItem(self.sTargetThree)
                    if self.sTargetFour != 0:
                        p.removeItem(self.sTargetFour)
                    for i in range(colorNumVal):
                        if i == 0:
                            self.sTargetOne = pg.ScatterPlotItem(x=colorXResult[0], y=colorYResult[0],
                                                                 brush=colorBlock[0], size=5)
                            p.addItem(self.sTargetOne)
                        elif i == 1:
                            self.sTargetTwo = pg.ScatterPlotItem(x=colorXResult[1], y=colorYResult[1],
                                                                 brush=colorBlock[1], size=5)
                            p.addItem(self.sTargetTwo)
                        elif i == 2:
                            self.sTargetThree = pg.ScatterPlotItem(x=colorXResult[2], y=colorYResult[2],
                                                                   brush=colorBlock[2], size=5)
                            p.addItem(self.sTargetThree)
                        elif i == 3:
                            self.sTargetFour = pg.ScatterPlotItem(x=colorXResult[3], y=colorYResult[3],
                                                                  brush=colorBlock[3], size=5)
                            p.addItem(self.sTargetFour)
                    self.oldXPositionVal = xPositionVal

                    # 核运行时间
                    self.z71OperationTime, self.z72OperationTime = self.operationTime.get_operation_time()
                    self.z71lineEdit.setText(str(self.z71OperationTime))
                    self.z72lineEdit.setText(str(self.z72OperationTime))

        if self.comboBoxCurrVal == 'Object' or self.comboBoxCurrVal == 'Debug':
            if horizontalPositionVal != [] and horizontalPositionVal != 0:
                #不是第一次画图
                if self.oldHorizontalPositionVal != 0:
                    if horizontalPositionVal != self.oldHorizontalPositionVal:
                        #清除target模式到object模式时的target，但要是在Object模式
                        if self.comboBoxCurrVal == 'Object':
                            if self.sTargetOne != 0:
                                p.removeItem(self.sTargetOne)
                            if self.sTargetTwo != 0:
                                p.removeItem(self.sTargetTwo)
                            if self.sTargetThree != 0:
                                p.removeItem(self.sTargetThree)
                            if self.sTargetFour != 0:
                                p.removeItem(self.sTargetFour)

                            # 核运行时间
                            self.z71OperationTime, self.z72OperationTime = self.operationTime.get_operation_time()
                            self.z71lineEdit.setText(str(self.z71OperationTime))
                            self.z72lineEdit.setText(str(self.z72OperationTime))

                        #显示object
                        #没有按键按下
                        if self.keyPressVal == 0:
                            p.removeItem(self.sObject)
                            if self.sTarget != 0:
                                p.removeItem(self.sTarget)
                            verticalPositionalValResult = [i * -1 for i in verticalPositionalVal]
                            self.sObject = pg.ScatterPlotItem(x=horizontalPositionVal, y=verticalPositionalValResult,
                                                              pen='y', brush='d0d0d0', size=10)
                            p.addItem(self.sObject)
                            self.oldHorizontalPositionVal = horizontalPositionVal
                            self.objectDataOld = self.objectData.get_completed_val()
                            self.oldObjectHorizontalPositionVal = horizontalPositionVal
                            self.oldObjectVerticalPositionalVal = verticalPositionalValResult
                            self.numObject = 0
                        #有按键按下
                        else:
                            self.oldHorizontalPositionVal = horizontalPositionVal
                            if self.numObject == 0:
                                self.numObject = 1
                else:
                    # 清除target模式到object模式时的target，但要是在Object模式
                    if self.comboBoxCurrVal == 'Object':
                        if self.sTargetOne != 0:
                            p.removeItem(self.sTargetOne)
                        if self.sTargetTwo != 0:
                            p.removeItem(self.sTargetTwo)
                        if self.sTargetThree != 0:
                            p.removeItem(self.sTargetThree)
                        if self.sTargetFour != 0:
                            p.removeItem(self.sTargetFour)
                    # 显示object
                    #第一次画图
                    verticalPositionalValResult = [i * -1 for i in verticalPositionalVal]
                    self.sObject = pg.ScatterPlotItem(x=horizontalPositionVal, y=verticalPositionalValResult, pen='y', brush='c7c7c7', size=10)
                    p.addItem(self.sObject)
                    self.oldHorizontalPositionVal = horizontalPositionVal

                    # 核运行时间
                    self.z71OperationTime, self.z72OperationTime = self.operationTime.get_operation_time()
                    self.z71lineEdit.setText(str(self.z71OperationTime))
                    self.z72lineEdit.setText(str(self.z72OperationTime))
#颜色区分是从深色到浅色
def color_classify(rcsIndex, rcsNum, xPositionVal, yPositionVal):
    colorXResult = []
    colorYResult = []
    singleColorX = []
    singleColorY = []
    if rcsNum < 4:
        for i in range(rcsNum):
            singleColorX.append(xPositionVal[rcsIndex[i]])
            singleColorY.append(yPositionVal[rcsIndex[i]])
            colorXResult.append(singleColorX)
            colorYResult.append(singleColorY)
            singleColorX = []
            singleColorY = []
        return colorXResult, colorYResult
    else:
        averageColor = rcsNum // 4
        #第一个色度
        for i in range(averageColor):
            singleColorX.append(xPositionVal[rcsIndex[i]])
            singleColorY.append(yPositionVal[rcsIndex[i]])
        colorXResult.append(singleColorX)
        colorYResult.append(singleColorY)
        singleColorX = []
        singleColorY = []
        # 第二个色度
        for i in range(averageColor):
            singleColorX.append(xPositionVal[rcsIndex[i + averageColor]])
            singleColorY.append(yPositionVal[rcsIndex[i + averageColor]])
        colorXResult.append(singleColorX)
        colorYResult.append(singleColorY)
        singleColorX = []
        singleColorY = []
        # 第三个色度
        for i in range(averageColor):
            singleColorX.append(xPositionVal[rcsIndex[i + averageColor * 2]])
            singleColorY.append(yPositionVal[rcsIndex[i + averageColor * 2]])
        colorXResult.append(singleColorX)
        colorYResult.append(singleColorY)
        singleColorX = []
        singleColorY = []
        #第四个色度
        for i in range(rcsNum - averageColor * 3):
            singleColorX.append(xPositionVal[rcsIndex[i + averageColor * 3]])
            singleColorY.append(yPositionVal[rcsIndex[i + averageColor * 3]])
        colorXResult.append(singleColorX)
        colorYResult.append(singleColorY)
        singleColorX = []
        singleColorY = []
        return colorXResult, colorYResult


def colordisplayfunction(targetDataOld, xPositionVal, yPositionVal):
    #逆序排序rcs的值
    rcsIndex = np.argsort(-np.array(targetDataOld['rcs']))
    #一共有多少个target
    rcsNum = np.array(rcsIndex).shape[0]
    colorXResult, colorYResult = color_classify(rcsIndex, rcsNum, xPositionVal, yPositionVal)
    return colorXResult, colorYResult


class targetdata:
    def __init__(self):
        self.xPositionVal = 0
        self.yPositionVal = 0
        #实时获取的值
        self.targetDicVal = {'vUnit': [], 'rUnit': [], 'Amplitude': [], 'Noise': [], 'Azimuth': [], 'Elevation': [], 'v': [],
                             'r': [], 'rcs': [], 'rVar': [], 'vVar': [], 'angleVar': [], 'rcsVar': [], 'noiseEnv': [], 'confidence': []}
        #获取成功的值存储的方法
        self.targetDicCompletedVal = 0

        #target num的值
        self.targetNum = 0

    def write_data(self, x, y):
        self.xPositionVal = x
        self.yPositionVal = y

    def get_data(self):
        return self.xPositionVal, self.yPositionVal, self.targetDicVal

    def write_target_dic_val(self, vUnit, rUnit, Amplitude, Noise, Azimuth, Elevation, v, r, rcs, rVar, vVar, angleVar, rcsVar, noiseEnv, confidence):
        self.targetDicVal['vUnit'].append(vUnit)
        self.targetDicVal['rUnit'].append(rUnit)
        self.targetDicVal['Amplitude'].append(Amplitude)
        self.targetDicVal['Noise'].append(Noise)
        self.targetDicVal['Azimuth'].append(Azimuth)
        self.targetDicVal['Elevation'].append(Elevation)
        self.targetDicVal['v'].append(v)
        self.targetDicVal['r'].append(r)
        self.targetDicVal['rcs'].append(rcs)
        self.targetDicVal['rVar'].append(rVar)
        self.targetDicVal['vVar'].append(vVar)
        self.targetDicVal['angleVar'].append(angleVar)
        self.targetDicVal['rcsVar'].append(rcsVar)
        self.targetDicVal['noiseEnv'].append(noiseEnv)
        self.targetDicVal['confidence'].append(confidence)

    def clear_target_dic_val(self):
        self.targetDicVal = {'vUnit': [], 'rUnit': [], 'Amplitude': [], 'Noise': [], 'Azimuth': [], 'Elevation': [],
                             'v': [], 'r': [], 'rcs': [], 'rVar': [], 'vVar': [], 'angleVar': [], 'rcsVar': [], 'noiseEnv': [],
                             'confidence': []}

    def write_completed_val(self, value):
        self.targetDicCompletedVal = value

    def get_completed_val(self):
        return self.targetDicCompletedVal

    def clear_completed_val(self):
        self.targetDicCompletedVal = 0

    def write_target_num(self, value):
        self.targetNum = value

    def get_target_num(self):
        return self.targetNum

class objectdata:
    def __init__(self):
        self.horizontalPositionVal = 0
        self.verticalPositionVal = 0
        #实时获取的值
        self.objectDicVal = {'tracingNum': [], 'tracingLabel': [], 'tracingStatus': [], 'horizontalDis': [], 'horizontalVel': [],
                             'verticalDis': [], 'verticalVel': [], 'horizontalAcc': [], 'verticalAcc': [], 'possibilityOfExist': [],
                             'classClassify': [], 'classMoveStatus': [], 'rcsVal': [], 'objectHeading': [], 'objectLength': [],
                             'objectWidth': []}
        # 获取成功的值存储的方法
        self.objectDicCompletedVal = 0

    def write_data(self, x, y):
        self.horizontalPositionVal = x
        self.verticalPositionVal = y

    def get_data(self):
        return self.horizontalPositionVal, self.verticalPositionVal, self.objectDicVal

    def write_object_dic_val(self, tracingNumVal, tracingLabelVal, tracingStatusVal, horizontalDisVal, horizontalVelVal,
                             verticalDisVal, verticalVelVal, horizontalAccVal, verticalAccVal, possibilityOfExistVal,
                             classClassifyVal, classMoveStatusVal, rcsVal, objectHeadingVal, objectLengthVal, objectWidthVal):
        self.objectDicVal['tracingNum'].append(tracingNumVal)
        self.objectDicVal['tracingLabel'].append(tracingLabelVal)
        self.objectDicVal['tracingStatus'].append(tracingStatusVal)
        self.objectDicVal['horizontalDis'].append(horizontalDisVal)
        self.objectDicVal['horizontalVel'].append(horizontalVelVal)
        self.objectDicVal['verticalDis'].append(verticalDisVal)
        self.objectDicVal['verticalVel'].append(verticalVelVal)
        self.objectDicVal['horizontalAcc'].append(horizontalAccVal)
        self.objectDicVal['verticalAcc'].append(verticalAccVal)
        self.objectDicVal['possibilityOfExist'].append(possibilityOfExistVal)
        self.objectDicVal['classClassify'].append(classClassifyVal)
        self.objectDicVal['classMoveStatus'].append(classMoveStatusVal)
        self.objectDicVal['rcsVal'].append(rcsVal)
        self.objectDicVal['objectHeading'].append(objectHeadingVal)
        self.objectDicVal['objectLength'].append(objectLengthVal)
        self.objectDicVal['objectWidth'].append(objectWidthVal)

    def clear_object_dic_val(self):
        self.objectDicVal = {'tracingNum': [], 'tracingLabel': [], 'tracingStatus': [], 'horizontalDis': [],
                            'horizontalVel': [], 'verticalDis': [], 'verticalVel': [], 'horizontalAcc': [], 'verticalAcc': [],
                            'possibilityOfExist': [], 'classClassify': [], 'classMoveStatus': [], 'rcsVal': [], 'objectHeading': [],
                            'objectLength': [], 'objectWidth': []}

    def write_completed_val(self, value):
        self.objectDicCompletedVal = value

    def get_completed_val(self):
        return self.objectDicCompletedVal

    def clear_completed_val(self):
        self.objectDicCompletedVal = 0