from xlwt import Workbook
import os
import time
import global_variable as gv
def CreateWorkbook(): #这里要有括号
    wbk = Workbook(encoding="utf-8")
    return wbk

def CloseWorkbook(wbk, ExcelName):
    FileName = str(ExcelName) + '_' + time.strftime("(%H%M%S)")+ ".xls"
    ExcelPath = os.path.join(os.path.dirname(gv.get_variable("biaoding_wenjian")), FileName)
    #wbk.save(r'C:\Users\Lee\Desktop\SysCalibration.xlsx')  # 保存
    wbk.save(ExcelPath)  # 保存

def CreateSheet(wbk, name):
    datasheet = wbk.add_sheet(name)
    return datasheet










