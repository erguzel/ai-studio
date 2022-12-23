import os
import sys
print(os.getcwd())
sys.path.insert(1,os.getcwd())


import pytest 

from src.aistudio.data.text_utils import *

def test_clear_default_chars():
    data = np.array([
        b'some data without any sign',
        b'special character data & ^',
        b'multiple    spaces data',
        b'SoME CApital LETTERS   and  spaces WitH  $p3c!@l Ch@r@ct3rs data'
    ])
    
    #Case1

    actual = np.array([
        'some data without any sign',
        'special character data',
        'multiple spaces data',
        'some capital letters and spaces with p3c ch ct3rs data'
    ])
    expected = clear_default_chars(data=data)
    assert len(actual) == len(expected)
    assert all([a==b for a,b in zip(actual,expected)])
    #
    #
    #
from nltk.stem import WordNetLemmatizer, LancasterStemmer
def test_stemming_lematization():
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
    expected = stemming_lematization(stem_or_lemmatizer=WordNetLemmatizer(),data=data)
    assert len(actual) == len(expected)
    assert all([a==b for a,b in zip(actual,expected)])
    #
    # Case2
    #
    actual = np.array([
        'som dat without any sign',
        'spec charact dat',
        'multipl spac dat',
        'som capit let and spac with p3c ch ct3rs dat'
    ])
    expected = stemming_lematization(stem_or_lemmatizer= LancasterStemmer(),data=data)
    assert len(actual) == len(expected)
    assert all([a==b for a,b in zip(actual,expected)])
    
