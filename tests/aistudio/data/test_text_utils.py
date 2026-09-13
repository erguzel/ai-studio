import numpy as np
import pytest

from aistudio.data.text_utils import clear_default_chars, stemming_lematization


class FakeLemmatizer:
    """Stands in for nltk's WordNetLemmatizer: strips a trailing 's'."""

    def lemmatize(self, token):
        return token[:-1] if token.endswith('s') else token


class FakeStemmer:
    """Stands in for an nltk StemmerI: keeps the first four characters."""

    def stem(self, token):
        return token[:4]


class FakeBoth(FakeLemmatizer, FakeStemmer):
    """Exposes both methods, so lemmatize has to win."""


def test_clear_default_chars_cleans_byte_texts():
    data = np.array([
        b'some data without any sign',
        b'special character data & ^',
        b'multiple    spaces data',
        b'SoME CApital LETTERS   and  spaces WitH  $p3c!@l Ch@r@ct3rs data',
    ])

    assert list(clear_default_chars(data=data)) == [
        'some data without any sign',
        'special character data',
        'multiple spaces data',
        'some capital letters and spaces with p3c ch ct3rs data',
    ]


def test_clear_default_chars_rejects_non_arrays():
    with pytest.raises(TypeError):
        clear_default_chars(data=['some data'])


def test_stemming_lematization_lemmatizes():
    data = np.array(['multiple spaces data', 'special characters'])

    result = stemming_lematization(stem_or_lemmatizer=FakeLemmatizer(), data=data)

    assert list(result) == ['multiple space data', 'special character']


def test_stemming_lematization_stems():
    data = np.array(['multiple spaces data', 'special characters'])

    result = stemming_lematization(stem_or_lemmatizer=FakeStemmer(), data=data)

    assert list(result) == ['mult spac data', 'spec char']


def test_stemming_lematization_prefers_lemmatize_over_stem():
    data = np.array(['multiple spaces'])

    result = stemming_lematization(stem_or_lemmatizer=FakeBoth(), data=data)

    assert list(result) == ['multiple space']


def test_stemming_lematization_rejects_non_arrays():
    with pytest.raises(TypeError):
        stemming_lematization(stem_or_lemmatizer=FakeLemmatizer(), data=['some data'])


def test_stemming_lematization_rejects_objects_without_either_method():
    with pytest.raises(TypeError):
        stemming_lematization(stem_or_lemmatizer=object(), data=np.array(['data']))
