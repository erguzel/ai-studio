import re as re
import numpy as np
from nltk.stem import WordNetLemmatizer, StemmerI
from exchelp.exception_helper import *



def stemming_lematization(stem_or_lemmatizer:WordNetLemmatizer|StemmerI,data : np.ndarray)->np.ndarray:
    """Stemmizes or lemmatizes the given data according to provided stemmer or lemmatizer.
    StemmerI or WordNetLemmatizer objects are accepted currently from nltk package

    Args:
        stem_or_lemmatizer (WordNetLemmatizer | StemmerI): instance of lemmatizer or stemmer object
        data (np.ndarray): 1d the data in (x,) shape

    Returns:
        np.ndarray: returns the lemmatized or stemmized tokens per each text
    """
    try:
        
        correctkDataType:bool = check_type(data,np.ndarray,TypeCheckMode.SUBTYPE) 
        if(not correctkDataType):
            raise CoreException(f'Data has to be a ndarray not {data.__class__.__name__}')

        correctStemmerLemmatizerDataType:bool = check_type(stem_or_lemmatizer,StemmerI,TypeCheckMode.SUBTYPE) or \
        check_type(stem_or_lemmatizer,WordNetLemmatizer,TypeCheckMode.TYPE)
        
        if(not correctStemmerLemmatizerDataType):
            raise CoreException(f'Stemmer or lemmatizer has to be StemmerI or WordnetLemmatizer not {stem_or_lemmatizer.__class__.__name__}')


        if(check_type(stem_or_lemmatizer,WordNetLemmatizer,TypeCheckMode.TYPE)):
            action = lambda k: ' '.join(stem_or_lemmatizer.lemmatize(token) for token in str(k).split())

        if(check_type(stem_or_lemmatizer,StemmerI,TypeCheckMode.SUBTYPE)):
            action = lambda k: ' '.join(stem_or_lemmatizer.stem(token) for token in str(k).split())
        
        act = np.vectorize(action)
        data = act(data)

        return data
        
    except Exception as e:
        CoverException('stemming_lematization function execution failed',e,logIt=True,dontThrow=True,shouldExit=True).adddata('local',locals()).act()
        #
        #
        #
def clear_default_chars(
    data: np.ndarray
    )->np.ndarray:
    """Clears given text array from unuseful characters for recognition
    multiple spaces, single letters, special characters, byte prefixes
    trims the text and uncapitalize/

    Args:
        data (np.ndarray): text array

    Returns:
        np.ndarray: char-wise cleared text array
    """
    try:
        if not check_type(data,np.ndarray,TypeCheckMode.SUBTYPE):
            raise CoreException(f'data must be np.ndarray not {data.__class__.__name__}')
        #remove special characters
        removeSpecials = lambda k : re.sub(r'\W', ' ', str(k))
        rsp = np.vectorize(removeSpecials)
        data = rsp(data)
        #remove single characters
        removeSingleCharacters = lambda k : re.sub(r'\s+[a-zA-Z]\s+', ' ', str(k))
        rsc = np.vectorize(removeSingleCharacters)
        data = rsc(data)
        #remove multiple spaces
        removeMultiSpaces = lambda k : re.sub(r'\s+', ' ', str(k), flags=re.I)
        rmsp = np.vectorize(removeMultiSpaces)
        data = rmsp(data)
        #remove byte prefix
        removingBytePrefix = lambda k : re.sub(r'^b\s+', '', str(k))
        rbtpfx = np.vectorize(removingBytePrefix)
        data = rbtpfx(data)
        #lower case
        lowerCase = lambda k: str(k).lower()
        lcs = np.vectorize(lowerCase)
        data = lcs(data)
        #trim text
        stripText = lambda k: str(k).strip()
        stx = np.vectorize(stripText)
        data = stx(data)
    except Exception as e:
        CoverException('clear_default_chars function failed',cause=e,logIt=True,shouldExit=True).act()
    
    return data
     