import datetime
#创建生成excel文档的名称
def create_excel_sn():
    # year = datetime.datetime.now().year
    # writeYear = year % 100
    # #一共2位，不足补零
    # writeYear = "%02d" % writeYear
    # month = datetime.datetime.now().month
    # month = "%02d" % month
    # day = datetime.datetime.now().day
    # day = "%02d" % day

    my_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 一共6位，不足补零
    excelSnNameVal = '标定结果_' + my_time
    return excelSnNameVal

