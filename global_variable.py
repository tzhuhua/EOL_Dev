'''该module主要是创建了一个全局变量的字典，在字典里面存入需要的值，以便在不同module之间传递value'''

def _init():
    '''只需要在main函数中运行一次即可'''
    global _dict
    _dict = {}
def set_variable(key, value):
    '''在字典中传入值'''
    _dict[key] = value
def get_variable(key):
    '''从字典里面取值'''
    try:
        return _dict[key]
    except KeyError:
        print('KeyError, 没有找到相应的Key!')