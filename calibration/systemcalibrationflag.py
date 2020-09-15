'''
系统标定是否做了
'''

def _init():
    global sysCaliFlag
    sysCaliFlag = {"flag":0}

def writeFlag(val):
    sysCaliFlag["flag"] = val

def getFlag():
    return sysCaliFlag["flag"]


