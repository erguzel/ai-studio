"""
contins util functions related to runtime
"""
import numpy as np
import exchelp.exception_helper as eh
from exchelp.exception_helper import *
from aistudio.abstraction.base_types import *

def is_array(variable):
    return isinstance(variable, list)  or isinstance(variable,np.ndarray)

def parametize_argsbase(
        param_arg:argsbase,
        defaultvalue,
        numofreplication=0,
        filllast = False #:TODO
        )-> argsbase:

    #None case
    result = []
    if not param_arg:
        [result.append(defaultvalue) for i in range(numofreplication)]
        return argsbase(*result)

    if  hasattr(param_arg,'masterparam'):
        if param_arg.masterparam():
            [result.append(param_arg) for i in range(numofreplication)]
            return argsbase(*result)
    else:
        [result.append(param_arg) for i in range(numofreplication)]
        return argsbase(*result)
    
    lenargs = len (param_arg.args)

    # replace Nones with default
    (
        [result.append(param_arg.args[j] if param_arg.args[j] else defaultvalue)
          if j < lenargs else result.append(defaultvalue)
            for j in range(numofreplication)]
    )
    
    return argsbase(*result)
        