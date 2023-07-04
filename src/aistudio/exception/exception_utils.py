import sys
from aistudio.abstraction.base_types import *
from aistudio.data.json.json_utils import *


class Interrupter(tpkwargsbase,Exception,BaseException):

    def __init__(self, *args, **kwargs):
        """
            Thrown in try block when an exception case caught.
        
            kwargs:
            log: logs exception as serialized json
            exit: exits app before throwing actual exception
            throw: throws actual exception
        """
        super().__init__(*args, **kwargs)

    def act(self, innerexception=None):
        """Orders final action of the exception according to previously given kwargs.

        Returns:
            None: Depending on given kwargs, perform log, exit, throw actions
        """
        acceptedactions = ('True','true','TRUE', True)

        if 'log' in self.kwargs:
            if  self.kwargs['log'] in acceptedactions:
                print(json.dumps(self,cls=JsonEncoders.DefaultJsonEncoder,indent=2))
        if 'exit' in self.kwargs:
            if self.kwargs['exit'] in acceptedactions:
                sys.exit('System is interrupted with a raised interruption object. Program is ended by user before raising the actual exception.')
        if 'throw' in self.kwargs:
            if self.kwargs['throw'] in acceptedactions:
                raise innerexception if innerexception else self

class InterruptPatcher(Interrupter):
    def __init__(self, *args, **kwargs):
        """
            Thrown in catch block to control the caught exceptions further.
        
            kwargs:
            log: logs exception as serialized json
            exit: exits app before throwing actual exception
            throw: throws actual exception
        """
        super().__init__(*args, **kwargs)

    def act(self,innerexception):
        """Orders final action of the exception according to previously given kwargs.

        Args:
            innerexception (BaseException): Inner exception caught in catch block

        Returns:
            None: Depending on given kwargs, perform log, exit, throw actions
        """
        self.innerexception = innerexception
        return super().act(innerexception=innerexception)

class Reporter():
    def __init__(self, **kwargs) -> None:
        self.__dict__ = self.__dict__ | kwargs
    def adddata(self,**kwargs):
        #self.__dict__ = self.__dict__ | kwargs
        for k,v in kwargs.items():
            self.__dict__[k] = v.__dict__ if hasattr(v,'__dict__') else v
        return self
    def getdata(self, key):
        if key not in self.__dict__:
            Interrupter('Given key {} does not exists in the Reporter object'.format(key)).addkvp(log = True,throw = True).act()
        return self.__dict__[key]

    def toJson(self,verbose = False):
        js = json.dumps(self,cls = JsonEncoders.DefaultJsonEncoder,indent=2)
        if verbose:
            print(js)
        else:return js
