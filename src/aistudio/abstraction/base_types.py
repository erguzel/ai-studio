
class baseall(object):
    def __init__(self) -> None:
        pass

    def isin(self, *keyorelms):
        if hasattr(self,'kwargs'):
            for key in keyorelms:
                if key in self.kwargs:
                    return True
        if hasattr(self,'args'):
            for key in keyorelms:
                if key in self.args:
                    return True
        return False
    
class kwargsbase(baseall):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        baseall.__init__(self)
    
    def addkvp(self,**kwargs):
        self.kwargs = self.kwargs | kwargs
        return self
    
    def popkvp(self,*keys)->tuple:
        """Mutates the kwargsbase object

        Returns:
            tuple: values of given keys
        """
        lenkeys = len(keys)
        res = []
        for i in range(lenkeys):
            if keys[i] in self.kwargs:
                v = self.kwargs.pop(keys[i])
                res.append((keys[i],v))
            else: res.append((keys[i],None))
        return tuple(res) if lenkeys>1 else res[0]

    def popval(self,*keys)->tuple:
        lenkeys = len(keys)
        res = []
        for i in range(len(keys)):
            if keys[i] in self.kwargs:
                v = self.kwargs.pop(keys[i])
                res.append(v)
            else:res.append(None)
        return tuple(res) if lenkeys>1 else res[0]

    def getval(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
            if keys[i] in self.kwargs:
                v = self.kwargs(keys[i])
                res.append(v)
            else: res.append(None)
        return tuple(res) if lenkeys>1 else res[0] 
        
    def getkvp(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
            if keys[i] in self.kwargs:
                kvpair = (keys[i],self.kwargs[keys[i]])
                res.append(kvpair)
            else: res.append(None)
        return tuple(res) if lenkeys>1 else res[0]
        

class argsbase(baseall):
    def __init__(self,*args):
        self.args = args
        baseall.__init__(self)
    
    def addelm(self, *args):
        self.args = self.args + args
        return self

    def rmvatidx(self,*index)->None:
        """
        Mutates argsbase object
        """
        self.args = tuple(self.args[i] for i in range(len(self.args)) if i not in index)
    
    def rmvelm(self,*elms)->None:
        """
        Mutates argsbase object
        """
        self.args = tuple(self.args[i] for i in range(len(self.args)) if self.args[i] not in elms)  

    def getelm(self,*index):
        return tuple(self.args[i] for i in range(len(self.args)) if i in index)


class argskwargssbase(argsbase,kwargsbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)  
        
        






