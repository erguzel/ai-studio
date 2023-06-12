"""
contins util functions related to runtime
"""
import numpy as np
import exchelp.exception_helper as eh
from exchelp.exception_helper import CoreException

  

def is_tuple(variable):
    return isinstance(variable, tuple)  

def is_array(variable):
    return isinstance(variable, list)  or isinstance(variable,np.ndarray)

def is_tuple(variable):
    return isinstance(variable, tuple)  

def is_str(variable):
    return isinstance(variable, str)

def param_itemize(param_s, maxlength, expectedtypes, defaultvalue=None):

    len_param_s = len(param_s) if is_array(param_s) else 1

    param_s = [defaultvalue for i in range(maxlength)] if not param_s else (
            [param_s for i in range(maxlength)] if eh.check_type(param_s,expectedtypes,eh.TypeCheckMode.SUBTYPE) else (
                ([(param_s[i] if param_s[i] else defaultvalue) if i == 0 else defaultvalue  for i in range(maxlength)] if len_param_s == 1 else [ (param_s[i] if param_s[i] else defaultvalue) if i < len_param_s else defaultvalue  for i in range(maxlength)] ) if is_array(param_s) else (
                    CoreException('There is an error mapping {} objects -> {} to desired plots.'.format(defaultvalue.__class__,expectedtypes),dontThrow=False,logIt=True,shouldExit=False).act()
                )
            )
        )
    
    for param in param_s:
        if(param):
            if(not eh.check_type(param,expectedtypes,eh.TypeCheckMode.SUBTYPE)):
                (
                    CoreException('There is an error mapping {} objects -> {} to desired plots.'.format(defaultvalue.__class__,expectedtypes),dontThrow=True,logIt=True,shouldExit=True)
                    .adddata("__WARN__",'some items {} are not in expected types of {}'.format(param.__class__,expectedtypes))
                    .act()
                )

    return param_s
