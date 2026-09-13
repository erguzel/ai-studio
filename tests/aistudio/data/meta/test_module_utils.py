import json

import numpy as np
import pytest

from aistudio.data.meta.module_utils import ModuleMeta, object_from_module


def test_object_from_module_resolves_a_function():
    assert object_from_module('json', 'dumps') is json.dumps


def test_object_from_module_resolves_a_sub_object():
    assert object_from_module('json', 'JSONEncoder', 'default') is json.JSONEncoder.default


def test_object_from_module_raises_on_unknown_module():
    with pytest.raises(ImportError):
        object_from_module('aistudio.no.such.module', 'anything')


def test_object_from_module_raises_on_unknown_object():
    with pytest.raises(AttributeError):
        object_from_module('json', 'no_such_object')


def test_module_meta_keeps_the_names_it_resolved():
    meta = ModuleMeta(moduleName='json', objectName='dumps')

    assert meta.modulename == 'json'
    assert meta.objectName == 'dumps'
    assert meta.subobjectName is None


def test_module_meta_caller_runs_the_resolved_function():
    """The declare-by-name path the examples rely on, without importing the callee."""
    caller = ModuleMeta(
        moduleName='aistudio.data.text_utils',
        objectName='clear_default_chars',
    ).caller

    result = caller(data=np.array([b'multiple    spaces data']))

    assert list(result) == ['multiple spaces data']
