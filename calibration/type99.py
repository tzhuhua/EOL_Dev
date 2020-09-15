
def type99(ListValueMessage, CanVariable):
    if ListValueMessage[0][0] == 0x636:
        if ListValueMessage[0][1] == 0xC1 and ListValueMessage[0][2] == 0x99:
            CanVariable.changeOperationStatus(0)






