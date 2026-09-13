import json
from decimal import Decimal

import numpy as np
import pytest

from aistudio.data.meta.module_utils import (
    ModuleMeta,
    instantiate,
    is_spec,
    object_from_module,
    resolve_spec,
)


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


def test_is_spec_needs_both_keys():
    assert is_spec({'module': 'decimal', 'object': 'Decimal'})
    assert not is_spec({'module': 'decimal'})
    assert not is_spec({'object': 'Decimal'})
    assert not is_spec('decimal.Decimal')


def test_resolve_spec_returns_the_object_uncalled():
    assert resolve_spec({'module': 'json', 'object': 'dumps'}) is json.dumps


def test_resolve_spec_follows_sub_objects():
    assert resolve_spec(
        {'module': 'json', 'object': 'JSONEncoder', 'subObject': 'default'}
    ) is json.JSONEncoder.default


def test_resolve_spec_rejects_non_specs():
    with pytest.raises(TypeError):
        resolve_spec({'module': 'json'})


def test_instantiate_calls_a_spec_with_its_hyper_params():
    value = instantiate({
        'module': 'decimal',
        'object': 'Decimal',
        'hyper_params': {'value': '1.5'},
    })

    assert value == Decimal('1.5')


def test_instantiate_calls_a_spec_without_hyper_params():
    assert instantiate({'module': 'decimal', 'object': 'Decimal'}) == Decimal(0)


def test_instantiate_resolves_specs_nested_in_hyper_params():
    """The reason this exists: a spec whose params name other objects."""
    value = instantiate({
        'module': 'collections',
        'object': 'Counter',
        'hyper_params': {
            'a': {'module': 'decimal', 'object': 'Decimal', 'hyper_params': {'value': '2'}},
        },
    })

    assert value['a'] == Decimal('2')


def test_instantiate_walks_dicts_and_lists():
    value = instantiate({
        'kept': 'as is',
        'numbers': [1, {'module': 'decimal', 'object': 'Decimal', 'hyper_params': {'value': '3'}}],
    })

    assert value['kept'] == 'as is'
    assert value['numbers'] == [1, Decimal('3')]


def test_instantiate_leaves_plain_values_untouched():
    assert instantiate(42) == 42
    assert instantiate('english') == 'english'
    assert instantiate(None) is None

