import os
import sys
print(os.getcwd())
sys.path.insert(1,os.getcwd())

from src.aistudio.data.meta.module_utils import ModuleMeta

import pytest 

from src.aistudio.data.text_utils import *

def test_module_meta():
    data = np.array([
        'some data without any sign',
        'special character data',
        'multiple spaces data',
        'some capital letters and spaces with p3c ch ct3rs data'
    ])
    
    # Case1
    
    actual = np.array([
        'some data without any sign',
        'special character data',
        'multiple space data',
        'some capital letter and space with p3c ch ct3rs data'
    ])

    #import aistudio.data.text_utils as tt
    #tt.stemming_lematization(WordNetLemmatizer())
    #ModuleMeta('nltk.stem','WordNetLemmatizer').get()
    lemmatizer_instance = ModuleMeta(
        moduleName='nltk.stem',
        objectName='WordNetLemmatizer').caller()
    res = ModuleMeta(
        'aistudio.data.text_utils',
        'stemming_lematization').caller
    
    result = res(stem_or_lemmatizer=lemmatizer_instance,data=data)

    print(result)

    



     

test_module_meta()