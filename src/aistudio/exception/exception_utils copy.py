#exchelp
# Includes exception types to handle exceptions and report carriers
#
from __future__ import annotations
import json
import socket
import sys
from enum import Enum
from  datetime import  datetime




"""
Static helper methods for exception handling
"""
class ExceptionHelpers:

    @staticmethod
    def jsonize(exception:Exception) ->str:
        """
        Jsonizes exception object
        :param exception: exception to jsonize
        :return: Json string as exception
        """
        try:
            exception.__dict__["_class"]=exception.__class__.__name__
            cause:Exception = exception.__cause__;
            if(cause != None):
                if(len(cause.__str__())>0):
                    cause.__dict__["_repr"]=cause.__repr__()
                    exception.__dict__["_cause"] = {key: val for key, val in dictionarize_data(cause).items() if key not in ["_env"]}

            filteredDict = {key: val for key, val in dictionarize_data(exception).items() }

            return json_dumps_safe(filteredDict)
        except Exception as e:
            raise TypeError('ExceptionHelper.jsonize failed',e)
            #
            #
            #
class CoreException(Exception,BaseException):
    """General Core reason exception, thrown after logical checks

    Args:
        Exception (_type_): Inherited from
        BaseException (_type_): Inherited from 
    """
    def __init__(self,message:str=None,cause:Exception=None,dontThrow:bool=False,logIt:bool=False,shouldExit:bool=False):
        """
        Initializes core exception object
        :param message: exception message
        :param cause: exception cause as exception
        :param dontThrow: true if it is not to be thrwn at act function call
        :param logIt: true if it is to be logged at act funciton call
        """

        """
        frameinfo = getframeinfo(currentframe())

print(frameinfo.filename, frameinfo.lineno)
        """

        self.message=message
        self.__cause__= cause
        self.dontthrow = dontThrow
        self.logit = logIt
        self.__initLineNo__()
        self.shouldexit = shouldExit
        #
        #
        #
    def __initLineNo__(self):
        """
        checks already thrown exception at the time of initialization
        get file and line info from sys.exc_info call
        """
        exception_type, exception_object, exception_traceback = sys.exc_info()
        if (exception_traceback != None):
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            self.__dict__['_file'] = filename
            self.__dict__['_line'] = line_number
            #
            #
            #
    def actwithlineandfile(self,lineNo,module):
        """
        Adds line number and module name to dict object before calling act method
        """
        if(not self.__dict__.__contains__('_line')):
            self.__dict__['_line'] = lineNo

        if(not  self.__dict__.__contains__('_file')):
            self.__dict__['_file']=module

        self.act()
        #
        #
        #
    def act(self):
        """
        acts according to log or throw boolean
        throws itself if throw boolean true at the moment of act function
        logs exception if log boolean true at the moment of act function
        :return: nothing
        """
        self.__dict__['_timeStamp']=datetime.now().__str__()
        self.__dict__['_env']= socket.gethostname()
        if(self.logit):
            print(ExceptionHelpers.jsonize(self))

        if(not self.dontthrow):
            raise self
        
        if(self.shouldexit):
            exit(-1)
            #
            #
            #
    def adddata(self,key:object, value:object):
        """
        Adds data to dict object
        """
        self.__dict__[key] = value
        return self
        #
        #
        #
    def getdata(self,key:object):
        try:
            res = self.__dict__[key]
            return res
        except Exception as e:
            TypeError('getData failed',e)
            #
            #
            #
    def shouldlog(self,shouldLog:bool):
        """
        Sets loggin boolean
        :param shouldlog: true if exception to be logged as json in act function call
        :return: nothing
        """
        self.logit = shouldLog
        return self
        #
        #
        #
    def shouldthrow(self,shouldThrow:bool):
        """
        Sets throw boolean
        :param shouldthrow: true if throw itself in act function call
        :return: nothing
        """
        self.dontthrow = not shouldThrow
        return self
        #
        #
        #
    def shouldexit(self,shouldExit:bool):
        """
        Sets exit boolean
        :param shouldexit: if true exit appliation at act function call
        :return: nothing
        """
        self.dontthrow = not shouldExit
        return self
        #
        #
        #

"""
Thworn for covering user thrown CoreExceptions or unknown system errors or exceptions
Set actual exception as cause in catch block
"""
class CoverException(CoreException):
    def __init__(self,message:str,cause:Exception=None,dontThrow:bool=False,logIt:bool=False,shouldExit = False):
        """
        Initializes object
        :param message: Exception message
        :param cause: Exception cause as exception
        :param dontThrow: true if it is not to be thrown
        :param logIt: true if exceptionto be logged as json
        """
        super(CoverException, self)\
            .__init__(message=message,cause=cause,dontThrow=dontThrow,logIt=logIt,shouldExit=shouldExit)
            #
            #
            #
# Util objects
#def check_type(instance: object, ttype:type,typecheckmode: TypeCheckMode = TypeCheckMode.TYPE,shouldthrow=False,
#               shouldlog:bool=False,file:str=None,line:int=None)->bool:
#

#
# Enums related to exception handling
#

class ReportObject(object):
    def __init__(self):
        """
        Initializes report object
        :param title: object title
        """
        #
        #
        #
    def adddata(self,key:object, value:object):
        """
        Adds data to dict object
        """
        self.__dict__[key] = value.__dict__ if hasattr(value,"__dict__") else value
        return self
        #
        #
        #
    def getdata(self,key:object)->ReportObject|dict|object:
        """Gets data from body dictionary

        Args:
            key (object): property name

        Returns:
            ReportObject|dict|object: property value
        """
        try:
            res = self.__dict__[key]
            return res
        except Exception as e:
            CoreException('getData failed',e,dontThrow=True,logIt=True,shouldExit=True).act()

    def __repr__(self) -> str:
        return 'ReportObject()'
        #
        #
        #
    def reportize(self,verbose:bool=False)->str:
        """converts class attributes to a json report

        Returns:
            _type_: json string from attributes of the class
        """
        if(verbose):
            print(json_dumps_safe(self))
            return
        return json_dumps_safe(self)
        #
        #
        #
class TypeCheckMode(Enum):
    TYPE = 1
    SUBTYPE = 2
    #
    #
    #
def check_type(instance: object, ttype:type,typecheckmode: TypeCheckMode = TypeCheckMode.TYPE)->bool:
    """
    checks the instance type if it matches with ttype
    :param instance: variable to check type
    :param ttype: the type to be compared
    :param typecheckmode: check mode: TYPE checks with type() method
                                      SUBTYPE checks with isinstance() method
    :param strictmode: throws exception if true when type mismatch detected
    :return: True if types are matching
    """
    try:
        if typecheckmode == TypeCheckMode.SUBTYPE:
            if type(ttype) is tuple:
                if None in ttype:
                    raise TypeError('None can not be a candidate for a subtype check. Use type mode instead for None check')
        
        if typecheckmode == TypeCheckMode.TYPE:
            if type(ttype) != type:
                raise TypeError('ttype must be a type for a type check')

        match typecheckmode:
            case TypeCheckMode.SUBTYPE:
                return isinstance(instance,ttype)
            case TypeCheckMode.TYPE:
                return type(instance) ==  ttype
            case _:
                TypeError(f'Given enum type {typecheckmode} is in default value')       
    except Exception as e:
        raise  TypeError(f"Type checking failed",e)

def try_get_dump(data,indent=2)->None|str:
    try:
        return json.dumps(data,indent=indent)
    except:
        return None
        #
        #
        #
def is_jsondumpable(data)->bool:
    try:
        json.dumps(data)
        return True
    except:
        return False
        #
        #
        #
def json_dumps_safe(data,indent=2):
    try:
        stringified= dictionarize_data(data=data)
        jsonized = json.dumps(stringified,indent=indent)
        return jsonized
    except Exception as e:
        raise TypeError('json_dumps_safe failed',e)
        #
        #
        #
def dictionarize_data(data)->dict:
  try:
     if is_jsondumpable(data) :return data 
     ### understand types
     isBytes = check_type(data,bytes,TypeCheckMode.SUBTYPE)
     if isBytes:
         return dictionarize_data(data=str(data))
     isByteArray = check_type(data,bytearray,TypeCheckMode.SUBTYPE)
     if isByteArray:
         return dictionarize_data(data=str(bytes(data)))
     isSet = hasattr(data,'issuperset') and hasattr(data,'issubset') and hasattr(data,'isdisjoint')
     if isSet:
         return dictionarize_data(data=list(data))
     hasDict = hasattr(data,'__dict__')
     if hasDict:
         isException = check_type(data,(Exception,BaseException),TypeCheckMode.SUBTYPE)
         if(isException):
            data.__dict__['_repr']=repr(data)
         return dictionarize_data(data=data.__dict__)
     isTuple = check_type(data,tuple,TypeCheckMode.SUBTYPE)
     if isTuple:
         return dictionarize_data(data=list(data))
     ## try iterate
     try:
         for idx, el in enumerate(data):
             isDict = hasattr(data,'items') and hasattr(data,'keys') and hasattr(data,'values')
             val = data[el] if isDict else data[idx]
             val = dictionarize_data(data=val)
             data[el if isDict else idx] = val
         data = dictionarize_data(data=data)
     except Exception as e:## not iterable meaning unguessed type
         data = dictionarize_data(data='<not-serializable>')
     return data
  except Exception as e:
    raise TypeError('dictionarize_data failed',e)


def test_function(data):
     return'printing {}'.format(data)
    



