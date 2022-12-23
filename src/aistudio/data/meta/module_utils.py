from importlib import import_module
from exchelp.exception_helper import CoverException


class ModuleMeta:
    def __init__(self,moduleName:str,objectName:str,subObjectName:str=None) -> None:
        self.modulename = moduleName
        self.objectName = objectName
        self.subobjectName = subObjectName
        self.caller = object_from_module(moduleName=self.modulename,objectName=self.objectName,subObjectName=self.subobjectName)
        
       

def object_from_module(moduleName:str,objectName:str,subObjectName:str=None):
    """Creates an instantiable meata-object of given module and object names combination

    Args:
        moduleName (str): name of the module
        objectName (str): name of the class or function
        subObjectName (str, optional): Name of the sub class or function. Defaults to None.

    Returns:
        _type_: a meta-object ready to be instantiated  """
    try:
        module = import_module(moduleName)
        result_ = getattr(module, objectName)
        if(subObjectName != None):
            result_ = getattr(result_,subObjectName)
        return result_
    except Exception as e:
        CoverException('object_from_module failed',e,dontThrow=True,logIt=True,shouldExit=True).adddata('locals',locals()).act()