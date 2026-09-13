from importlib import import_module


class ModuleMeta:
    def __init__(self,moduleName:str,objectName:str,subObjectName:str|None=None) -> None:
        self.modulename = moduleName
        self.objectName = objectName
        self.subobjectName = subObjectName
        self.caller = object_from_module(
            moduleName=self.modulename,
            objectName=self.objectName,
            subObjectName=self.subobjectName,
        )
        
       

def object_from_module(moduleName:str,objectName:str,subObjectName:str|None=None):
    """Resolves the named object of the named module without instantiating it.

    Args:
        moduleName (str): name of the module
        objectName (str): name of the class or function
        subObjectName (str, optional): Name of the sub class or function. Defaults to None.

    Returns:
        The resolved class or function, ready to be called.

    Raises:
        ImportError: if the module cannot be imported.
        AttributeError: if the module has no such object.
    """
    module = import_module(moduleName)
    result_ = getattr(module, objectName)
    if subObjectName is not None:
        result_ = getattr(result_,subObjectName)
    return result_
