"""
contins util functions related to runtime
"""
import numpy as np
import exchelp.exception_helper as eh
from exchelp.exception_helper import *
from aistudio.abstraction.base_types import *

  

def is_tuple(variable):
    return isinstance(variable, tuple)  

def is_array(variable):
    return isinstance(variable, list)  or isinstance(variable,np.ndarray)

def is_tuple(variable):
    return isinstance(variable, tuple)  

def is_str(variable):
    return isinstance(variable, str)

def param_itemize(param_s, maxlength, expectedtypes, defaultvalue=None):
    """
    Only for primitive types. Fills the rest of the array with default values
    Suitable for functions which can run with trivial default or empty args or kwargs
    """

    len_param_s = len(param_s) if is_array(param_s) else 1

    param_s = [defaultvalue for i in range(maxlength)] if not param_s else (
            [param_s for i in range(maxlength)] if eh.check_type(param_s,expectedtypes,eh.TypeCheckMode.SUBTYPE) else (
                ([(param_s[i] if param_s[i] else defaultvalue) if i == 0 else defaultvalue  for i in range(maxlength)] if len_param_s == 1 else [ (param_s[i] if param_s[i] else defaultvalue) if i < len_param_s else defaultvalue  for i in range(maxlength)] ) if is_array(param_s) else (
                    CoreException('There is an error mapping {} objects -> {} to desired plots.'.format(defaultvalue.__class__,expectedtypes),logIt=True).act()
                )
            )
        )
    
    for param in param_s:
        if(param):
            if(not eh.check_type(param,expectedtypes,eh.TypeCheckMode.SUBTYPE)):
                (
                    CoreException('There is an error mapping {} objects -> {} to desired plots.'.format(defaultvalue.__class__,expectedtypes),logIt=True)
                    .adddata("__WARN__",'some items {} are not in expected types of {}'.format(param.__class__,expectedtypes))
                    .act()
                )

    return param_s


def param_itemize_type (param_t,maxlength, expectedtypes):
    """
    Itemization occurs without filling the rest of the array with default value. Therefore no default value is needed
    Output array length might differ.
    Suitable for functions that only to be executed if a spesified parameter is exists for it
    """
    len_param_t = len(param_t) if is_array(param_t) else 1

    if not param_t:
         return []

    if is_array(param_t):
        if len_param_t != maxlength:
            (
                CoreException('This parameter is a required for all corresponding number of paarameters defined my maxlength {}.'.format(maxlength),None,logIt=True,)
                .adddata('*','param_t length should match with the maxlength param.')
                .act()
            )
        if not all(param_t):
            (
                CoreException('This parameter is a required for all corresponding number of paarameters defined my maxlength {}.'.format(maxlength),None,logIt=True,)
                .adddata('*','All members of the param array must be a nonnull value.')
                .act()
            )

    # replicate for all 
    if eh.check_type(param_t,expectedtypes,eh.TypeCheckMode.SUBTYPE) :
        param_t = [param_t for i in range(maxlength)]
        return param_t
    

    for param in param_t:
        if(param):
            if(not eh.check_type(param,expectedtypes,eh.TypeCheckMode.SUBTYPE)):
                (
                    CoreException('There is an error mapping {} objects -> {} to desired plots.',None,logIt=True)
                    .adddata("__WARN__",'some items {} are not in expected types of {}'.format(param.__class__,expectedtypes))
                    .act()
                )

    return param_t