
class argsbase(object):
    def __init__(self) -> None:
        pass
    #oveeride
    def __len__(self):
        return len(self.kwargs) + len(self.args) if isinstance(self,tpkwargsbase) else\
        len(self.kwargs) if isinstance(self,kwargsbase) else len(self.args)
    #override
    def __contains__(self,item):
        if isinstance(self, kwargsbase):        
                if item in self.kwargs:
                    return True
        if isinstance(self,argsbase):
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

class kwargsbase(argsbase):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        argsbase.__init__(self)
    #override
    def __getitem__(self,key):
        return self.kwargs[key]
    #override
    def __setitem__(self,key,val):
        self.args[key] = val
    
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
                v = self.kwargs.pop(keys[i])
                res.append((keys[i],v))
        return tuple(res) if lenkeys>1 else res[0]

    def popval(self,*keys,nonsafe=True)->tuple:
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
    def getval(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
                v = self.kwargs[keys[i]]
                res.append(v)
        return tuple(res) if lenkeys>1 else res[0] 
        
    def getkvp(self,*keys)->tuple:
        res = []
        lenkeys = len(keys)
        for i in range(lenkeys):
      #      if keys[i] in self.kwargs:
                kvpair = (keys[i],self.kwargs[keys[i]])
                res.append(kvpair)
       #     else: res.append(None)
        return tuple(res) if lenkeys>1 else res[0]
        

class tpargsbase(argsbase):
    def __init__(self,*args):
        self.args = args
        argsbase.__init__(self)
    #override
    def __getitem__(self,index):
        return self.args[index] 

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
        res =  tuple(self.args[i] for i in range(len(self.args)) if i in index)
        return res if len(res) >1 else res[0]


class tpkwargsbase(tpargsbase,kwargsbase):
    def __init__(self,*args,**kwargs):
        tpargsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)  

    #override
    def __getitem__(self,key):
        return self.args[key] if isinstance(key,int) else self.kwargs[key]

        






