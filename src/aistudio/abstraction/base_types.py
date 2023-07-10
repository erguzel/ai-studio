
class argsbase(object):
    def __init__(self) -> None:
        pass

    #override
    def __str__(self) -> str:
        st =''
    
        st = f'[ args = {self.args}, kwargs = {self.kwargs} ]' if isinstance(self,dictuplargs) else\
        f'kwargs = {self.kwargs}' if isinstance(self,dictargs) else f'args = {self.args}'
        return st

    def __repr__(self) -> str:
         return str(self)

    #oveeride
    def __len__(self):
        return len(self.kwargs) + len(self.args) if isinstance(self,dictuplargs) else\
        len(self.kwargs) if isinstance(self,dictargs) else len(self.args)
    #override
    def __contains__(self,item):
        if isinstance(self, dictargs):        
                if item in self.kwargs:
                    return True
        if isinstance(self,tuplargs):
                if item in self.args:
                    return True
        return False
    def isin(self, *keyorelms):
        
        res = []
        lenkeyorelms = len(keyorelms)
        for keyorelm in keyorelms:
            if(self.__contains__(keyorelm)):
                res.append(True)
            else: res.append(False)

        return tuple(res) if lenkeyorelms >1 else res[0]

        """
        if hasattr(self,'kwargs'):
            for key in keyorelms:
                if key in self.kwargs:
                    return True
        if hasattr(self,'args'):
            for key in keyorelms:
                if key in self.args:
                    return True
        return False
        """

class dictargs(argsbase):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        argsbase.__init__(self)
    #override
    def __getitem__(self,key):
        return self.kwargs[key]
    #override
    def __setitem__(self,key,val):
        self.kwargs[key] = val
    
    def addkvps(self,**kwargs):
        self.kwargs = self.kwargs | kwargs
        return self
    
    def popkvps(self,*keys)->tuple:
        """Mutates the kwargsbase object

        Returns:
            tuple: values of given keys
        """
        lenkeys = len(keys)
        res = []
        for i in range(lenkeys):
                v = self.kwargs.pop(keys[i])
                res.append((keys[i],v))
        return tuple(res) if lenkeys>1 else res[0]

    def popvals(self,*keys,nonsafe=True)->tuple:
        lenkeys = len(keys)
        res = []

        if nonsafe:
             for i in range(len(keys)):
                if keys[i] in self.kwargs:
                    v = self.kwargs.pop(keys[i])
                    res.append(v)  
                       # kvpair = (keys[i],self.kwargs[keys[i]])
                       # res.append(kvpair)
                else: res.append(None)
        else:
             for i in range(len(keys)):
                v = self.kwargs.pop(keys[i])
                res.append(v)  
                
        return tuple(res) if lenkeys>1 else res[0]
                  
        """
        for i in range(len(keys)):
                if nonsafe:
                  if keys[i] in self.kwargs:
                        kvpair = (keys[i],self.kwargs[keys[i]])
                        res.append(kvpair)
                  else: res.append(None)
                else:
                    v = self.kwargs.pop(keys[i])
                    res.append(v)   
        """             
    def getvals(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
                v = self.kwargs[keys[i]]
                res.append(v)
        return tuple(res) if lenkeys>1 else res[0] 
        
    def getkvps(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
      #      if keys[i] in self.kwargs:
                kvpair = (keys[i],self.kwargs[keys[i]])
                res.append(kvpair)
       #     else: res.append(None)
        return tuple(res) if lenkeys>1 else res[0]
        

class tuplargs(argsbase):
    def __init__(self,*args):
        self.args = args
        argsbase.__init__(self)
    #override
    def __getitem__(self,index):
        return self.args[index] 

    def addelms(self, *args):
        self.args = self.args + args
        return self

    def rmvatidx(self,*index)->None:
        """
        Mutates argsbase object
        """
        self.args = tuple(self.args[i] for i in range(len(self.args)) if i not in index)
    
    def rmvelms(self,*elms)->None:
        """
        Mutates argsbase object
        """
        self.args = tuple(self.args[i] for i in range(len(self.args)) if self.args[i] not in elms)  

    def getelms(self,*index):
        res =  tuple(self.args[i] for i in range(len(self.args)) if i in index)
        return res if len(res) >1 else res[0]


class dictuplargs(tuplargs,dictargs):
    def __init__(self,*args,**kwargs):
        tuplargs.__init__(self,*args)
        dictargs.__init__(self,**kwargs)  

    #override
    def __getitem__(self,key):
        return self.args[key] if isinstance(key,int) else self.kwargs[key]

        






