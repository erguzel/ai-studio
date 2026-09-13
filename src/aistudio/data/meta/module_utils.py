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


def is_spec(value) -> bool:
    """Tells whether a value is an object spec.

    A spec is a dict naming an object to resolve: ``module`` and ``object`` are
    required, ``subObject`` and ``hyper_params`` are optional.

    Args:
        value: anything.

    Returns:
        bool: True if the value is a dict carrying both required keys.
    """
    return isinstance(value, dict) and 'module' in value and 'object' in value


def resolve_spec(spec: dict):
    """Resolves a spec to the object it names, without calling it.

    Use this for the functions and values a pipeline declares - a cleaner
    function to apply later, a constant to read. Use instantiate() instead when
    the spec names a class the pipeline wants an instance of.

    Args:
        spec (dict): a spec, as is_spec() defines it.

    Returns:
        The resolved class, function or value.

    Raises:
        TypeError: if the value is not a spec.
        ImportError: if the module cannot be imported.
        AttributeError: if the module has no such object.
    """
    if not is_spec(spec):
        raise TypeError(f'not an object spec: {spec!r}')
    return object_from_module(
        moduleName=spec['module'],
        objectName=spec['object'],
        subObjectName=spec.get('subObject'),
    )


def instantiate(value):
    """Builds the instances a declared pipeline asks for, however deeply nested.

    Every spec found is resolved and called with its own ``hyper_params``,
    themselves instantiated first - so a spec whose hyper_params name an
    optimizer, or a list of callbacks, comes back as an object holding real
    instances. Dicts and lists are walked; anything else is returned untouched.

    Args:
        value: a spec, or any structure of dicts and lists that may contain
            specs at any depth.

    Returns:
        The same structure with every spec replaced by an instance of what it
        names.

    Raises:
        ImportError: if a named module cannot be imported.
        AttributeError: if a named module has no such object.
    """
    if is_spec(value):
        return resolve_spec(value)(**instantiate(value.get('hyper_params', {})))
    if isinstance(value, dict):
        return {k: instantiate(v) for k, v in value.items()}
    if isinstance(value, list):
        return [instantiate(v) for v in value]
    return value
