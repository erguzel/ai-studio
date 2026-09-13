import copy
import json
from json import JSONEncoder

import numpy as np

from aistudio.abstraction.base_types import dictargs, tuplargs


class JsonEncoders:
    def __init__(self) -> None:
        pass
    
    class DefaultJsonEncoder(JSONEncoder):
        def default(self,o):
            try:
                if is_jsondumpable(o):
                    return o
                if isinstance(o,bytes):
                    return self.default(o=str(o))
                if isinstance(o,bytearray):
                    return self.default(o=str(bytes(o)))
                if isinstance(o,set):
                    return self.default(o=list(o))
                # numpy scalars: np.float64 subclasses float and is dumpable,
                # but np.int64 is not, so convert every numpy scalar here.
                if isinstance(o,np.generic):
                    return self.default(o=o.item())
                #
                if isinstance(o, JSNode):
                    return self.default(o = o.__data__)
                #
                if isinstance(o,dictargs):
                    return self.default(o = o.kwargs)
                #
                if isinstance(o,tuplargs):
                    return self.default(o=list(o.args))
                
                if hasattr(o,'__dict__'):
                    if isinstance(o,BaseException):
                        o.__dict__['_repr']=repr(o)
                    return self.default(o=o.__dict__)
                if isinstance(o,tuple):
                    return self.default(o=list(o))
                if isinstance(o,np.ndarray):
                    return self.default(o = list(o))
                ## try iterate
                try:
                    for idx, el in enumerate(o):
                        isDict = isinstance(o,dict)
                        val = o[el] if isDict else o[idx]
                        val = self.default(o=val)
                        o[el if isDict else idx] = val
                    o = self.default(o=o)
                except Exception:## not iterable meaning unguessed type
                    o = self.default(o='<not-serializable>')
                return o
            except Exception as e:
                raise TypeError('dictionarize_data failed',e) from e
            


def is_jsondumpable(data)->bool:
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def jsonize(
    data,
    verbose = False,
    fullsavename = None,
    encoder = JsonEncoders.DefaultJsonEncoder,
    indent = 2,
):
        js = json.dumps(data,cls = encoder,indent=indent)
        if verbose:
            print(js)
        if fullsavename:
            with open(fullsavename, 'w') as f:
                f.write(js)
        return js

class JSNode:
    def __init__(self, **kwargs) -> None:
        self.__data__ = dictargs(**kwargs)
    def update(self,**kwargs):
        #self.__dict__ = self.__dict__ | kwargs
        self.__data__.addkvps(**kwargs)
        #for k,v in kwargs.items():
        #    self.__data__[k] = v if is_typeof(Reporter) else \
        #        v.__dict__ if hasattr(v,'__dict__') else v
        return self
    def get_property(self, key):
        if key not in self.__data__:
            raise KeyError(f'Given key {key} does not exists in the Reporter object')
        return self.__data__[key]

    def del_property(self,key):
        if key not in self.__data__:
            raise KeyError(f'Given key {key} does not exists in the Reporter object')
        self.__data__.popkvps(key)
        return self
    
    def toJson(self,verbose = True):
        
        data = copy.deepcopy(self)
        js = json.dumps(data,cls = JsonEncoders.DefaultJsonEncoder,indent=2)
        if verbose:
            print(js)
        return js
