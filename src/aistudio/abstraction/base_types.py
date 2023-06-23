
class baseall(object):
    def __init__(self) -> None:
        self.__masterparam__ = False
    def setmasterparam(self,ismaster:bool):
        self.__masterparam__ = ismaster
        return self
    def masterparam(self):
        return self.__masterparam__


class kwargsbase(baseall):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        baseall.__init__(self)

    def rmv(self,*keys):
        for key in keys:
            if key in self.kwargs:
                return self.kwargs.pop(key)

class argsbase(baseall):
    def __init__(self,*args):
        self.args = args
        baseall.__init__(self)

class argskwargssbase(argsbase,kwargsbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)  
        






