import os
import xlrd
import time
from xlutils.copy import copy
from .createdoc import CreateWorkbook
from .createdoc import CloseWorkbook
from .createdoc import CreateSheet

#写角度标定的excel
def writedata(AngleSheet, CalcAngleList, AngleNum):
    # 方差值pass为0，fail为1
    varPassFail = 0

    AngleSheet.write(0, 0, "真实角度")
    AngleSheet.write(0, 1, "均值")
    AngleSheet.write(0, 2, "均值Limit")
    AngleSheet.write(0, 3, "方差")
    AngleSheet.write(0, 4, "方差Limit")
    AngleSheet.write(0, 5, "Pass/Fail")

    row = AngleNum + 2
    AngleSheet.write(row, 0, "真实角度/测量值")
    AngleSheet.write(row, 1, "目标1")
    AngleSheet.write(row, 2, "目标2")
    AngleSheet.write(row, 3, "目标3")
    AngleSheet.write(row, 4, "目标4")
    AngleSheet.write(row, 5, "目标5")
    AngleSheet.write(row, 6, "目标6")
    AngleSheet.write(row, 7, "目标7")
    AngleSheet.write(row, 8, "目标8")
    AngleSheet.write(row, 9, "目标9")
    AngleSheet.write(row, 10, "目标10")

    for i in range(AngleNum):
        CalcValue = []
        if CalcAngleList[i][1] >= 0x80:
            RealAngle = CalcAngleList[i][1] - 0x100
        else:
            RealAngle = CalcAngleList[i][1]

        for j in range(10):
            value = (CalcAngleList[i][3 + j * 2] << 8) | CalcAngleList[i][2 + j * 2]
            if value >= 0x8000:
                value = value - 0x10000
            value = value / 100
            CalcValue.append(value)

        AveValue = (CalcAngleList[i][23] << 8) | CalcAngleList[i][22]
        if AveValue >= 0x8000:
            AveValue = AveValue - 0x10000
        AveValue = AveValue / 100

        AveValueLimit = (CalcAngleList[i][25] << 8) | CalcAngleList[i][24]
        if AveValueLimit >= 0x8000:
            AveValueLimit = AveValueLimit - 0x10000
        AveValueLimit = AveValueLimit / 100

        VarValue = (CalcAngleList[i][27] << 8) | CalcAngleList[i][26]
        if VarValue >= 0x8000:
            VarValue = VarValue - 0x10000
        VarValue = VarValue / 100

        VarValueLimit = (CalcAngleList[i][29] << 8) | CalcAngleList[i][28]
        if VarValueLimit >= 0x8000:
            VarValueLimit = VarValueLimit - 0x10000
        VarValueLimit = VarValueLimit / 100

        PassFailValue = CalcAngleList[i][30]

        #角度
        AngleSheet.write(i+1, 0, RealAngle)
        AngleSheet.write(i+1 + AngleNum + 2, 0, RealAngle)

        #测量值
        AngleSheet.write(i+1 + AngleNum + 2, 1, CalcValue[0])
        AngleSheet.write(i+1 + AngleNum + 2, 2, CalcValue[1])
        AngleSheet.write(i+1 + AngleNum + 2, 3, CalcValue[2])
        AngleSheet.write(i+1 + AngleNum + 2, 4, CalcValue[3])
        AngleSheet.write(i+1 + AngleNum + 2, 5, CalcValue[4])
        AngleSheet.write(i+1 + AngleNum + 2, 6, CalcValue[5])
        AngleSheet.write(i+1 + AngleNum + 2, 7, CalcValue[6])
        AngleSheet.write(i+1 + AngleNum + 2, 8, CalcValue[7])
        AngleSheet.write(i+1 + AngleNum + 2, 9, CalcValue[8])
        AngleSheet.write(i+1 + AngleNum + 2, 10, CalcValue[9])

        #均值(limit)、方差(limit)
        AngleSheet.write(i+1, 1, AveValue)
        AngleSheet.write(i+1, 2, AveValueLimit)
        AngleSheet.write(i+1, 3, VarValue)
        AngleSheet.write(i+1, 4, VarValueLimit)

        # pass/fail
        if PassFailValue == 1:
            if VarValue <= 2:
                AngleSheet.write(i+1, 5, "Pass")
            else:
                AngleSheet.write(i + 1, 5, "Fail")
                varPassFail = 1
        else:
            AngleSheet.write(i+1, 5, "Fail")

    return varPassFail

#写角度标定的值
def writeanglecalibration(ExcelName, CalcAngleList, AngleNum, groupCanInfo):
    FileName = ExcelName + '_' + str(groupCanInfo) + time.strftime("(%H%M%S)")+".xls"
    ExcelPath = os.path.join("C:/标定/配置文件/", FileName)
    if os.path.exists(ExcelPath):
        wk = xlrd.open_workbook(ExcelPath, formatting_info=True)
        #新建sheet
        wb = copy(wk)
        AngleSheet = wb.add_sheet('角度标定')
        varPassFail = writedata(AngleSheet, CalcAngleList, AngleNum)
        wb.save(ExcelPath)
    else:
        wb = CreateWorkbook()
        AngleSheet = CreateSheet(wb, "角度标定")
        varPassFail = writedata(AngleSheet, CalcAngleList, AngleNum)
        CloseWorkbook(wb, ExcelName, groupCanInfo)  # 保存
    return varPassFail

def anglecalibration(AngleData, CalcAngleList):
    ValueRawList = []
    for value in AngleData:
        if value[0] == 1584 and value[1] == 0x2:
            for RawValue in value[-6:]:
                ValueRawList.append(RawValue)

    CalcAngleList.append(ValueRawList)



