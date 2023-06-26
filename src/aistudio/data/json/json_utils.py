
# {k:v for k,v in o.__dict__ if k not in exclude}
import json
from json import JSONEncoder

class JsonEncoders():
    def __init__(self) -> None:
        pass
    
    class DefaultJsonEncoder(JSONEncoder):
        def default(self,o):
            try:
                if is_jsondumpable(o) :return o 
                if isinstance(o,bytes):
                    return self.default(o=str(o))
                if isinstance(o,bytearray):
                    return self.default(o=str(bytes(o)))
                if isinstance(o,set):
                    return self.default(o=list(o))
                if hasattr(o,'__dict__'):
                    if isinstance(o,BaseException):
                        o.__dict__['_repr']=repr(o)
                    return self.default(o=o.__dict__)
                if isinstance(o,tuple):
                    return self.default(o=list(o))
                ## try iterate
                try:
                    for idx, el in enumerate(o):
                        isDict = isinstance(o,dict)
                        val = o[el] if isDict else o[idx]
                        val = self.default(o=val)
                        o[el if isDict else idx] = val
                    o = self.default(o=o)
                except Exception as e:## not iterable meaning unguessed type
                    o = self.default(o='<not-serializable>')
                return o
            except Exception as e:
                raise TypeError('dictionarize_data failed',e)
            


def is_jsondumpable(data)->bool:
    try:
        json.dumps(data)
        return True
    except:
        return False


    


