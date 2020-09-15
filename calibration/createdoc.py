from xlwt import Workbook
import os
import time

def CreateWorkbook(): #这里要有括号
    wbk = Workbook(encoding="utf-8")
    return wbk

def CloseWorkbook(wbk, ExcelName, groupCanInfo):
    FileName = str(ExcelName) + '_' + str(groupCanInfo) + time.strftime("(%H%M%S)")+ ".xls"
    ExcelPath = os.path.join("C:/标定/配置文件/", FileName)
    #wbk.save(r'C:\Users\Lee\Desktop\SysCalibration.xlsx')  # 保存
    wbk.save(ExcelPath)  # 保存

def CreateSheet(wbk, name):
    datasheet = wbk.add_sheet(name)
    return datasheet










