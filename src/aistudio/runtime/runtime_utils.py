"""
contins util functions related to runtime
"""
import numpy as np
from aistudio.abstraction.base_types import *
from aistudio.exception.exception_utils import *

def is_array(variable):
    return isinstance(variable, list)  or isinstance(variable,np.ndarray)

def parametize_tpargsbase(
        param_arg:tpargsbase,
        defaultvalue,
        numofreplication=0,
        metavals = tpargsbase('_masterparam','masterparam','__masterparam__','__masterparam'),
        )-> tpargsbase:

    #None case
    result = []
    if not param_arg:
        [result.append(defaultvalue) for i in range(numofreplication)]
        return tpargsbase(*result)

    if  isinstance(param_arg,argsbase):
        if any(param_arg.isin(*metavals.args)):
            if subtype_checker(param_arg,tpargsbase):
                param_arg.rmvelm(*metavals.args)
            if subtype_checker(param_arg,kwargsbase):
                param_arg.popval(*metavals.args)

            [result.append(param_arg) for i in range(numofreplication)]
            return tpargsbase(*result)
    else:
        [result.append(param_arg) for i in range(numofreplication)]
        return tpargsbase(*result)
    
    lenargs = len(param_arg)

    # replace Nones with default
    (
        [result.append(param_arg[j] if param_arg[j] else defaultvalue)
          if j < lenargs else result.append(defaultvalue)
            for j in range(numofreplication)]
    )
    
    return tpargsbase(*result)
    

def type_checker (instance, *types)->bool:
    """
    Checks the type of given instance is among the types provided.
    Does not check inner element types.
    
    Args:
        instance (Any): Instance variable
        *types (Type): a series of types i.e str,int,list

    Returns:
        bool: True if the instance type in types
    """
    for typ in types:
        if type(instance) == typ:
            return True
    return False

def subtype_checker(instance, *types)->bool:
    """
    Checks given instance type is type or a subtype of the given types

    Args:
        instance (Any): Instance variable
        *types (Type): a series of types i.e. str, int, dict

    Returns:
        bool: True if given instance type is among the given type args, or instance type is a subtype of given types
    """
    for typ in types:
        if isinstance(instance,typ):
            return True
    return False

