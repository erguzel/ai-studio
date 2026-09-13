"""The malaria example's CONFIG is checked here, not its training.

An example is only an example while it still runs. Nothing else covers the
declarations in its CONFIG: a renamed keras object, a moved module or a typo in
a spec would build nothing, and would only be noticed by someone running the
example on 27,558 images. These tests build each declared model and stop there.

Skipped unless tensorflow, matplotlib and scikit-learn are installed - the
example imports all three.
"""
import importlib.util
import sys
from copy import deepcopy
from pathlib import Path

import pytest

tf = pytest.importorskip('tensorflow', reason='needs the tf extra')
pytest.importorskip('matplotlib', reason='needed by the example')
pytest.importorskip('sklearn', reason='needed by the example')

from aistudio.model.keras_utils import build_model, fit_params  # noqa: E402

EXAMPLE = Path(__file__).resolve().parents[3] / 'examples' / 'malaria-detection'
CLASSES = ('Parasitized', 'Uninfected')


@pytest.fixture(scope='module')
def example():
    """Imports the example by path, with its own directory importable.

    By path because both examples name their entry point run_pipeline.py, and
    with the directory on sys.path because CONFIG names the example's own
    preprocessing module - which is the point of that declaration.
    """
    sys.path.insert(0, str(EXAMPLE))
    try:
        spec = importlib.util.spec_from_file_location(
            'malaria_run_pipeline', EXAMPLE / 'run_pipeline.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path.remove(str(EXAMPLE))


@pytest.fixture
def config(example):
    """The declared pipeline, with the pretrained weights left unfetched.

    What is under test is the declaration, not keras' ability to download 58 MB
    of ImageNet weights, so the transfer model is built from an untrained base.
    """
    config = deepcopy(example.CONFIG)
    config['models']['VGG16Transfer']['base_model']['hyper_params']['weights'] = None
    return config


def test_the_example_declares_the_three_architectures(config):
    assert list(config['models']) == ['BaseModel', 'Augmented', 'VGG16Transfer']


@pytest.mark.parametrize('name', ['BaseModel', 'Augmented', 'VGG16Transfer'])
def test_every_declared_model_builds_and_compiles(config, name):
    model = build_model(config['models'][name])

    assert model.compiled


@pytest.mark.parametrize('name', ['BaseModel', 'Augmented', 'VGG16Transfer'])
def test_every_model_takes_the_declared_images_and_answers_per_class(config, name):
    """The models declare no input shape, so keras builds them on first use."""
    model = build_model(config['models'][name])

    model.build((None, *config['initialize']['image_size'], 3))

    assert model.output_shape == (None, len(CLASSES))


def test_the_augmented_model_declares_augmentation_layers(config):
    kinds = [type(layer).__name__ for layer in build_model(config['models']['Augmented']).layers]

    assert 'RandomFlip' in kinds
    assert 'RandomRotation' in kinds


def test_the_plain_model_declares_no_augmentation(config):
    kinds = [type(layer).__name__ for layer in build_model(config['models']['BaseModel']).layers]

    assert 'RandomFlip' not in kinds


def test_the_example_preprocessing_layer_resolves_by_name(config):
    """CONFIG names a class of the example's own, not one of keras'."""
    model = build_model(config['models']['VGG16Transfer'])

    assert 'VGGPreprocessing' in [type(layer).__name__ for layer in model.layers]


def test_the_pretrained_base_is_declared_frozen(config):
    model = build_model(config['models']['VGG16Transfer'])
    trunk = next(layer for layer in model.layers if isinstance(layer, tf.keras.Model))

    assert trunk.trainable is False
    assert not any(id(weight) in {id(w) for w in trunk.weights}
                   for weight in model.trainable_weights)


def test_the_declared_callbacks_are_built(config):
    params = fit_params(config['models']['BaseModel'])

    stopping = params['callbacks'][0]
    assert isinstance(stopping, tf.keras.callbacks.EarlyStopping)
    assert stopping.restore_best_weights is True


def test_the_corpus_is_looked_for_inside_the_example(example):
    """Nothing in CONFIG should point at whoever ran it last."""
    assert Path(example.CONFIG['initialize']['source']).is_relative_to(EXAMPLE)
