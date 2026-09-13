import json

import numpy as np
import pytest

from aistudio.serialization.report import JSNode, is_jsondumpable, jsonize


def make_report():
    return JSNode(
        problem=JSNode(
            title='DATA_PATH',
            target='pickups',
            factors=['temporal', 'seasonal', 'geographical'],
        )
    )


def test_update_adds_keys_and_returns_self():
    report = make_report()

    assert report.update(data=JSNode(shape=(2, 3))) is report
    assert isinstance(report.get_property('data'), JSNode)


def test_get_property_raises_on_unknown_key():
    with pytest.raises(KeyError):
        make_report().get_property('missing')


def test_del_property_removes_the_key():
    report = make_report().update(data=JSNode(shape=(2, 3)))

    report.del_property('data')

    with pytest.raises(KeyError):
        report.get_property('data')


def test_del_property_raises_on_unknown_key():
    with pytest.raises(KeyError):
        make_report().del_property('missing')


def test_tojson_serializes_nested_nodes():
    report = make_report()

    assert json.loads(report.toJson(verbose=False)) == {
        'problem': {
            'title': 'DATA_PATH',
            'target': 'pickups',
            'factors': ['temporal', 'seasonal', 'geographical'],
        }
    }


def test_tojson_leaves_the_node_untouched():
    report = make_report()

    report.toJson(verbose=False)

    assert isinstance(report.get_property('problem'), JSNode)


def test_tojson_serializes_numpy_scalars_and_arrays():
    report = JSNode(
        samples=np.int64(42),
        score=np.float64(0.5),
        labels=np.array([1, 2, 3]),
    )

    assert json.loads(report.toJson(verbose=False)) == {
        'samples': 42,
        'score': 0.5,
        'labels': [1, 2, 3],
    }


def test_tojson_serializes_exceptions():
    report = JSNode(error=ValueError('boom'))

    assert 'boom' in json.loads(report.toJson(verbose=False))['error']['_repr']


def test_is_jsondumpable():
    assert is_jsondumpable({'a': 1})
    assert not is_jsondumpable(np.int64(1))


def test_jsonize_writes_the_file_it_is_given(tmp_path):
    target = tmp_path / 'report.json'

    js = jsonize(JSNode(samples=np.int64(42)), fullsavename=str(target))

    assert json.loads(target.read_text()) == {'samples': 42}
    assert json.loads(js) == {'samples': 42}
