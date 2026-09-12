import re

import numpy as np


def stemming_lematization(stem_or_lemmatizer, data: np.ndarray) -> np.ndarray:
    """Stem or lemmatize every text in the given array.

    Args:
        stem_or_lemmatizer: any object exposing either a ``lemmatize(token)``
            or a ``stem(token)`` method, such as nltk's ``WordNetLemmatizer``
            or any ``StemmerI`` implementation. ``lemmatize`` wins if both
            are present.
        data: 1d array of texts, shape (x,).

    Returns:
        The array with each text replaced by its stemmed or lemmatized tokens.

    Raises:
        TypeError: if data is not an ndarray, or the given object exposes
            neither method.
    """
    if not isinstance(data, np.ndarray):
        raise TypeError(f'data has to be an ndarray, not {type(data).__name__}')

    if hasattr(stem_or_lemmatizer, 'lemmatize'):
        reduce_token = stem_or_lemmatizer.lemmatize
    elif hasattr(stem_or_lemmatizer, 'stem'):
        reduce_token = stem_or_lemmatizer.stem
    else:
        raise TypeError(
            'stem_or_lemmatizer has to expose a lemmatize or stem method, '
            f'and {type(stem_or_lemmatizer).__name__} exposes neither'
        )

    reduce_text = lambda k: ' '.join(reduce_token(token) for token in str(k).split())

    return np.vectorize(reduce_text)(data)
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

    Raises:
        TypeError: if data is not an ndarray.
    """
    if not isinstance(data, np.ndarray):
        raise TypeError(f'data has to be an ndarray, not {type(data).__name__}')
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

    return data
