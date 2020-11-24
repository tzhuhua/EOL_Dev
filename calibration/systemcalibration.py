from .createdoc import CreateSheet


def syscalibration(CaliResultSetText, wb, CanVariable):
    CompList = []  # 补偿值 0x632
    AvgList = []  # 平均值 0x633
    RawList = []  # 原始数据 0x631
    PassFailList = []  # 0x634

    CompListValue = []
    AvgListValue = []
    RawData = []

    DisValueList = []
    VelValueList = []
    AmpValueList = []
    SnrValueList = []
    Para1ValueList = []
    Para2ValueList = []
    Para3ValueList = []
    Para4ValueList = []
    Para5ValueList = []
    Para6ValueList = []
    Para7ValueList = []
    Para8ValueList = []
    Para9ValueList = []
    Para10ValueList = []
    Para11ValueList = []
    Para12ValueList = []
    Para13ValueList = []
    Para14ValueList = []
    Para15ValueList = []
    Para16ValueList = []
    Calc1ValueList = []
    Calc2ValueList = []
    Calc3ValueList = []
    Calc4ValueList = []
    Calc5ValueList = []
    Calc6ValueList = []
    Calc7ValueList = []
    Calc8ValueList = []
    Calc9ValueList = []
    Calc10ValueList = []
    Calc11ValueList = []
    Calc12ValueList = []
    Calc13ValueList = []
    Calc14ValueList = []
    Calc15ValueList = []
    Calc16ValueList = []

    ListValueMessage = CanVariable.getListValueMessage()
    for value in ListValueMessage:
        if value[0] == 0x632:
            CompList.append(value)
        if value[0] == 0x633:
            AvgList.append(value)
        if value[0] == 0x631:
            RawList.append(value)
        if value[0] == 0x634:
            PassFailList.append(value)
    if not CompList or not AvgList or not PassFailList:
        message = "标定失败！未收到ID为632，633或634的报文， 请检查标定的距离！"
        return message
    if PassFailList:
        if PassFailList[0][3] == 1 and len(RawList) < 175:
            message = "标定成功！但是上位机未能收到全部报文，无法生成结果文件！"
            return message
    for value in CompList:
        if value[1] == 2:
            CompValue = (value[4] << 8) | value[3]
            if CompValue >= 0x8000:
                CompValue = CompValue - 0x10000
            CompValue = CompValue / 100
            CompListValue.append(CompValue)
            CompValue = (value[6] << 8) | value[5]
            if CompValue >= 0x8000:
                CompValue = CompValue - 0x10000
            CompValue = CompValue / 100
            CompListValue.append(CompValue)
            CompValue = (value[8] << 8) | value[7]
            if CompValue >= 0x8000:
                CompValue = CompValue - 0x10000
            CompValue = CompValue / 100
            CompListValue.append(CompValue)
    # print(CompListValue)

    for value in AvgList:
        if value[1] == 2:
            AvgValue = (value[4] << 8) | value[3]
            if AvgValue >= 0x8000:
                AvgValue = AvgValue - 0x10000
            AvgValue = AvgValue / 100
            AvgListValue.append(AvgValue)
            AvgValue = (value[6] << 8) | value[5]
            if AvgValue >= 0x8000:
                AvgValue = AvgValue - 0x10000
            AvgValue = AvgValue / 100
            AvgListValue.append(AvgValue)
            AvgValue = (value[8] << 8) | value[7]
            if AvgValue >= 0x8000:
                AvgValue = AvgValue - 0x10000
            AvgValue = AvgValue / 100
            AvgListValue.append(AvgValue)

    for value in RawList:
        if value[1] == 2:
            for RawValue in value[-6:]:
                RawData.append(RawValue)

    # print(np.shape(RawData))        # tuple没有shape  tuple->list：list()
    # print(RawData)
    ColValSum = []
    for i in range(10):
        ColValData = []
        ColValData = RawData[(i * 104):((i + 1) * 104)]
        # print(ColValData)
        ColValSum.append(ColValData)
    # print(ColValSum)

    for rawValue in ColValSum:
        # 距离
        value = (rawValue[1] << 8) | rawValue[0]
        value = value / 100
        DisValueList.append(value)
        # 速度
        value = (rawValue[3] << 8) | rawValue[2]
        if value >= 0x8000:
            value = value - 0x10000
        value = value / 100
        VelValueList.append(value)
        # 幅值
        value = (rawValue[5] << 8) | rawValue[4]
        if value >= 0x8000:
            value = value - 0x10000
        value = value / 100
        AmpValueList.append(value)
        # snr
        value = (rawValue[7] << 8) | rawValue[6]
        if value >= 0x8000:
            value = value - 0x10000
        value = value / 100
        SnrValueList.append(value)

        for i in range(16):
            value = (rawValue[11 + i * 4] << 24) | (rawValue[10 + i * 4] << 16) | (rawValue[9 + i * 4] << 8) | rawValue[
                8 + i * 4]
            if value >= 0x80000000:
                value = value - 0x100000000
            value = value / 100
            if i == 0:
                Para1ValueList.append(value)
            elif i == 1:
                Para2ValueList.append(value)
            elif i == 2:
                Para3ValueList.append(value)
            elif i == 3:
                Para4ValueList.append(value)
            elif i == 4:
                Para5ValueList.append(value)
            elif i == 5:
                Para6ValueList.append(value)
            elif i == 6:
                Para7ValueList.append(value)
            elif i == 7:
                Para8ValueList.append(value)
            elif i == 8:
                Para9ValueList.append(value)
            elif i == 9:
                Para10ValueList.append(value)
            elif i == 10:
                Para11ValueList.append(value)
            elif i == 11:
                Para12ValueList.append(value)
            elif i == 12:
                Para13ValueList.append(value)
            elif i == 13:
                Para14ValueList.append(value)
            elif i == 14:
                Para15ValueList.append(value)
            elif i == 15:
                Para16ValueList.append(value)

        for i in range(16):
            value = (rawValue[73 + i * 2] << 8) | rawValue[72 + i * 2]
            if value >= 0x80000000:
                value = value - 0x100000000
            value = value / 100
            if i == 0:
                Calc1ValueList.append(value)
            elif i == 1:
                Calc2ValueList.append(value)
            elif i == 2:
                Calc3ValueList.append(value)
            elif i == 3:
                Calc4ValueList.append(value)
            elif i == 4:
                Calc5ValueList.append(value)
            elif i == 5:
                Calc6ValueList.append(value)
            elif i == 6:
                Calc7ValueList.append(value)
            elif i == 7:
                Calc8ValueList.append(value)
            elif i == 8:
                Calc9ValueList.append(value)
            elif i == 9:
                Calc10ValueList.append(value)
            elif i == 10:
                Calc11ValueList.append(value)
            elif i == 11:
                Calc12ValueList.append(value)
            elif i == 12:
                Calc13ValueList.append(value)
            elif i == 13:
                Calc14ValueList.append(value)
            elif i == 14:
                Calc15ValueList.append(value)
            elif i == 15:
                Calc16ValueList.append(value)

    datasheet = CreateSheet(wb, "系统标定")

    datasheet.write(0, 0, "Data1")  # 第1行第1列数据
    datasheet.write(0, 1, "目标1")  # 第1行第2列数据
    datasheet.write(0, 2, "目标2")
    datasheet.write(0, 3, "目标3")
    datasheet.write(0, 4, "目标4")
    datasheet.write(0, 5, "目标5")
    datasheet.write(0, 6, "目标6")
    datasheet.write(0, 7, "目标7")
    datasheet.write(0, 8, "目标8")
    datasheet.write(0, 9, "目标9")
    datasheet.write(0, 10, "目标10")

    datasheet.write(1, 0, "距离")  # 第2行第1列数据
    datasheet.write(2, 0, "速度")
    datasheet.write(3, 0, "幅值")
    datasheet.write(4, 0, "SNR")
    datasheet.write(5, 0, "参数1")
    datasheet.write(6, 0, "参数2")
    datasheet.write(7, 0, "参数3")
    datasheet.write(8, 0, "参数4")
    datasheet.write(9, 0, "参数5")
    datasheet.write(10, 0, "参数6")
    datasheet.write(11, 0, "参数7")
    datasheet.write(12, 0, "参数8")
    datasheet.write(13, 0, "参数9")
    datasheet.write(14, 0, "参数10")
    datasheet.write(15, 0, "参数11")
    datasheet.write(16, 0, "参数12")
    datasheet.write(17, 0, "参数13")
    datasheet.write(18, 0, "参数14")
    datasheet.write(19, 0, "参数15")
    datasheet.write(20, 0, "参数16")
    datasheet.write(21, 0, "计算值1")
    datasheet.write(22, 0, "计算值2")
    datasheet.write(23, 0, "计算值3")
    datasheet.write(24, 0, "计算值4")
    datasheet.write(25, 0, "计算值5")
    datasheet.write(26, 0, "计算值6")
    datasheet.write(27, 0, "计算值7")
    datasheet.write(28, 0, "计算值8")
    datasheet.write(29, 0, "计算值9")
    datasheet.write(30, 0, "计算值10")
    datasheet.write(31, 0, "计算值11")
    datasheet.write(32, 0, "计算值12")
    datasheet.write(33, 0, "计算值13")
    datasheet.write(34, 0, "计算值14")
    datasheet.write(35, 0, "计算值15")
    datasheet.write(36, 0, "计算值16")

    datasheet.write(38, 0, "Data2")
    datasheet.write(39, 0, "补偿值1")
    datasheet.write(40, 0, "补偿值2")
    datasheet.write(41, 0, "补偿值3")
    datasheet.write(42, 0, "补偿值4")
    datasheet.write(43, 0, "补偿值5")
    datasheet.write(44, 0, "补偿值6")
    datasheet.write(45, 0, "补偿值7")
    datasheet.write(46, 0, "补偿值8")
    datasheet.write(47, 0, "补偿值9")
    datasheet.write(48, 0, "补偿值10")
    datasheet.write(49, 0, "补偿值11")
    datasheet.write(50, 0, "补偿值12")
    datasheet.write(51, 0, "补偿值13")
    datasheet.write(52, 0, "补偿值14")
    datasheet.write(53, 0, "补偿值15")
    datasheet.write(54, 0, "补偿值16")

    datasheet.write(56, 0, "Data3")
    datasheet.write(57, 0, "参数1 avg")
    datasheet.write(58, 0, "参数2 avg")
    datasheet.write(59, 0, "参数3 avg")
    datasheet.write(60, 0, "参数4 avg")
    datasheet.write(61, 0, "参数5 avg")
    datasheet.write(62, 0, "参数6 avg")
    datasheet.write(63, 0, "参数7 avg")
    datasheet.write(64, 0, "参数8 avg")
    datasheet.write(65, 0, "参数9 avg")
    datasheet.write(66, 0, "参数10 avg")
    datasheet.write(67, 0, "参数11 avg")
    datasheet.write(68, 0, "参数12 avg")
    datasheet.write(69, 0, "参数13 avg")
    datasheet.write(70, 0, "参数14 avg")
    datasheet.write(71, 0, "参数15 avg")
    datasheet.write(72, 0, "参数16 avg")

    datasheet.write(74, 0, "Data4")
    datasheet.write(75, 0, "Pass/Fail")
    datasheet.write(76, 0, "Fail类型")

    # 距离
    col = 1
    for value in DisValueList:
        datasheet.write(1, col, value)
        col += 1

    # 速度
    col = 1
    for value in VelValueList:
        datasheet.write(2, col, value)
        col += 1

    # 幅值
    col = 1
    for value in AmpValueList:
        datasheet.write(3, col, value)
        col += 1

    # SNR
    col = 1
    for value in SnrValueList:
        datasheet.write(4, col, value)
        col += 1

    # 参数1
    col = 1
    for value in Para1ValueList:
        datasheet.write(5, col, value)
        col += 1

    # 参数2
    col = 1
    for value in Para2ValueList:
        datasheet.write(6, col, value)
        col += 1

    # 参数3
    col = 1
    for value in Para3ValueList:
        datasheet.write(7, col, value)
        col += 1

    # 参数4
    col = 1
    for value in Para4ValueList:
        datasheet.write(8, col, value)
        col += 1

    # 参数5
    col = 1
    for value in Para5ValueList:
        datasheet.write(9, col, value)
        col += 1

    # 参数6
    col = 1
    for value in Para6ValueList:
        datasheet.write(10, col, value)
        col += 1

    # 参数7
    col = 1
    for value in Para7ValueList:
        datasheet.write(11, col, value)
        col += 1

    # 参数8
    col = 1
    for value in Para8ValueList:
        datasheet.write(12, col, value)
        col += 1

    # 参数9
    col = 1
    for value in Para9ValueList:
        datasheet.write(13, col, value)
        col += 1

    # 参数10
    col = 1
    for value in Para10ValueList:
        datasheet.write(14, col, value)
        col += 1

    # 参数11
    col = 1
    for value in Para11ValueList:
        datasheet.write(15, col, value)
        col += 1

    # 参数12
    col = 1
    for value in Para12ValueList:
        datasheet.write(16, col, value)
        col += 1

    # 参数13
    col = 1
    for value in Para13ValueList:
        datasheet.write(17, col, value)
        col += 1

    # 参数14
    col = 1
    for value in Para14ValueList:
        datasheet.write(18, col, value)
        col += 1

    # 参数15
    col = 1
    for value in Para15ValueList:
        datasheet.write(19, col, value)
        col += 1

    # 参数16
    col = 1
    for value in Para16ValueList:
        datasheet.write(20, col, value)
        col += 1

    # 计算值1
    col = 1
    for value in Calc1ValueList:
        datasheet.write(21, col, value)
        col += 1

    # 计算值2
    col = 1
    for value in Calc2ValueList:
        datasheet.write(22, col, value)
        col += 1

    # 计算值3
    col = 1
    for value in Calc3ValueList:
        datasheet.write(23, col, value)
        col += 1

    # 计算值4
    col = 1
    for value in Calc4ValueList:
        datasheet.write(24, col, value)
        col += 1

    # 计算值5
    col = 1
    for value in Calc5ValueList:
        datasheet.write(25, col, value)
        col += 1

    # 计算值6
    col = 1
    for value in Calc6ValueList:
        datasheet.write(26, col, value)
        col += 1

    # 计算值7
    col = 1
    for value in Calc7ValueList:
        datasheet.write(27, col, value)
        col += 1

    # 计算值8
    col = 1
    for value in Calc8ValueList:
        datasheet.write(28, col, value)
        col += 1

    # 计算值9
    col = 1
    for value in Calc9ValueList:
        datasheet.write(29, col, value)
        col += 1

    # 计算值10
    col = 1
    for value in Calc10ValueList:
        datasheet.write(30, col, value)
        col += 1

    # 计算值11
    col = 1
    for value in Calc11ValueList:
        datasheet.write(31, col, value)
        col += 1

    # 计算值12
    col = 1
    for value in Calc12ValueList:
        datasheet.write(32, col, value)
        col += 1

    # 计算值13
    col = 1
    for value in Calc13ValueList:
        datasheet.write(33, col, value)
        col += 1

    # 计算值14
    col = 1
    for value in Calc14ValueList:
        datasheet.write(34, col, value)
        col += 1

    # 计算值15
    col = 1
    for value in Calc15ValueList:
        datasheet.write(35, col, value)
        col += 1

    # 计算值16
    col = 1
    for value in Calc16ValueList:
        datasheet.write(36, col, value)
        col += 1

    # 补偿值
    row = 39
    for value in CompListValue:
        datasheet.write(row, 1, value)
        row += 1
        if row == 55:
            break

    # 参数1 avg
    row = 57
    for value in AvgListValue:
        datasheet.write(row, 1, value)
        row += 1
        if row == 73:
            break

    # Pass/Fail
    # print(PassFailList)
    if PassFailList[0][3] == 0:
        datasheet.write(75, 1, "Fail")
        FailValue = "Fail:" + str(PassFailList[0][4])
        CaliResultSetText.setText(FailValue)
    elif PassFailList[0][3] == 1:
        datasheet.write(75, 1, "Pass")
        #CaliResultSetText.setText("Pass")
    datasheet.write(76, 1, PassFailList[0][3])
    return "成功"






