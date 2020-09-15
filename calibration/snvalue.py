import datetime

def create_sn_list(snValue, batchNum, clientCode):
    year = datetime.datetime.now().year
    writeYear = year % 100
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    snValue = int(snValue)
    snLowByte = snValue & 0xff
    snMiddleByte = (snValue & 0xff00) >> 8
    snHighByte = (snValue & 0xff0000) >> 16

    batchNum = int(batchNum)
    batchNumLowByte = batchNum & 0xff
    batchNumMiddleByte = (batchNum & 0xff00) >> 8
    batchNumHighByte =  (batchNum & 0xff0000) >> 16

    snList = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
    clientCodeList = list(clientCode)
    i = 0
    for value in clientCodeList:
        snList[i] = ord(value)
        i = i + 1

    actualList = []
    singleList = [0x02, 0x03, 23, 0x54, writeYear, month, day, 0x42]
    actualList.append(singleList)
    singleList = [0x02, 0x03, 18, snHighByte, snMiddleByte, snLowByte, 0x53, batchNumHighByte]
    actualList.append(singleList)
    singleList = [0x02, 0x03, 13, batchNumMiddleByte, batchNumLowByte, 0x23, snList[0], snList[1]]
    actualList.append(singleList)
    singleList = [0x02, 0x03, 8, snList[2], snList[3], snList[4], snList[5], snList[6]]
    actualList.append(singleList)
    singleList = [0x02, 0x03, 3, snList[7], snList[8], snList[9], 0x0, 0x0]
    actualList.append(singleList)

    return actualList

#创建生成excel文档的名称
def create_excel_sn(batchNum, canSnNumber, clientCode):
    year = datetime.datetime.now().year
    writeYear = year % 100
    #一共2位，不足补零
    writeYear = "%02d" % writeYear
    month = datetime.datetime.now().month
    month = "%02d" % month
    day = datetime.datetime.now().day
    day = "%02d" % day
    # 一共6位，不足补零
    batchNumVal = batchNum.zfill(6)
    canSnNumberVal = canSnNumber.zfill(6)
    excelSnNameVal = 'T' + str(writeYear) + str(month) + str(day) + 'B' + batchNumVal + 'S' + canSnNumberVal + '#' + clientCode
    return excelSnNameVal

