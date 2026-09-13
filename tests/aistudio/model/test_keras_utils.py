"""Keras helper tests; skipped unless the tf extra is installed."""
import pytest

tf = pytest.importorskip('tensorflow', reason='needs the tf extra')

import numpy as np  # noqa: E402 - only reached when tensorflow is there

from aistudio.model.keras_utils import (  # noqa: E402
    build_model,
    build_sequential_model,
    build_transfer_model,
    fit_params,
)

LAYERS = [
    {'module': 'tensorflow.keras.layers', 'object': 'Conv2D',
     'hyper_params': {'filters': 4, 'kernel_size': 2, 'padding': 'same',
                      'activation': 'relu', 'input_shape': (8, 8, 3)}},
    {'module': 'tensorflow.keras.layers', 'object': 'MaxPooling2D',
     'hyper_params': {'pool_size': 2}},
    {'module': 'tensorflow.keras.layers', 'object': 'Flatten'},
    {'module': 'tensorflow.keras.layers', 'object': 'Dense',
     'hyper_params': {'units': 2, 'activation': 'softmax'}},
]

COMPILE = {
    'loss': 'categorical_crossentropy',
    'optimizer': {'module': 'tensorflow.keras.optimizers', 'object': 'Adam',
                  'hyper_params': {'learning_rate': 0.001}},
    'metrics': ['accuracy'],
}

SPEC = {'layers': LAYERS, 'compile': COMPILE}


@pytest.fixture
def dataset():
    rng = np.random.default_rng(0)
    images = rng.random((16, 8, 8, 3)).astype('float32')
    labels = tf.keras.utils.to_categorical(rng.integers(0, 2, 16), 2)
    return images, labels


def test_layers_are_built_in_the_declared_order():
    model = build_sequential_model(SPEC, compile_model=False)

    assert [type(layer).__name__ for layer in model.layers] == [
        'Conv2D', 'MaxPooling2D', 'Flatten', 'Dense']


def test_hyper_params_reach_the_layers():
    model = build_sequential_model(SPEC, compile_model=False)

    assert model.layers[0].filters == 4
    assert model.layers[-1].units == 2


def test_the_optimizer_is_instantiated_not_named():
    model = build_sequential_model(SPEC)

    assert isinstance(model.optimizer, tf.keras.optimizers.Adam)
    assert float(model.optimizer.learning_rate) == pytest.approx(0.001)


def test_a_compiled_model_trains(dataset):
    images, labels = dataset
    model = build_sequential_model(SPEC)

    history = model.fit(images, labels, epochs=1, batch_size=8, verbose=0)

    assert 'loss' in history.history


def test_a_model_is_not_compiled_when_asked_not_to_be():
    model = build_sequential_model(SPEC, compile_model=False)

    assert not model.compiled


def test_transfer_models_continue_the_named_layer():
    spec = {
        'base_model': {'module': 'tensorflow.keras.applications', 'object': 'VGG16',
                       'hyper_params': {'weights': None, 'include_top': False,
                                        'input_shape': (32, 32, 3)}},
        'base_layer': 'block3_pool',
        'layers': [
            {'module': 'tensorflow.keras.layers', 'object': 'Flatten'},
            {'module': 'tensorflow.keras.layers', 'object': 'Dense',
             'hyper_params': {'units': 2, 'activation': 'softmax'}},
        ],
        'compile': COMPILE,
    }

    model = build_transfer_model(spec)

    names = [layer.name for layer in model.layers]
    assert 'block3_pool' in names
    assert 'block4_conv1' not in names  # the rest of VGG16 is left behind
    assert model.output_shape == (None, 2)


def test_build_model_dispatches_on_the_spec():
    assert build_model(SPEC, compile_model=False).__class__.__name__ == 'Sequential'


def test_fit_params_instantiate_the_callbacks():
    params = fit_params({'fit': {
        'epochs': 3,
        'callbacks': [{'module': 'tensorflow.keras.callbacks', 'object': 'EarlyStopping',
                       'hyper_params': {'monitor': 'val_loss', 'patience': 4}}],
    }})

    assert params['epochs'] == 3
    assert isinstance(params['callbacks'][0], tf.keras.callbacks.EarlyStopping)
    assert params['callbacks'][0].patience == 4


def test_fit_params_of_a_spec_without_fit():
    assert fit_params({'layers': LAYERS}) == {}


def test_a_built_model_survives_being_saved(tmp_path, dataset):
    from aistudio.model.model_utils import save_model

    images, _ = dataset
    model = build_sequential_model(SPEC)
    path = str(tmp_path / 'model.keras')

    save_model(model, path)
    reloaded = tf.keras.models.load_model(path)

    assert np.allclose(model.predict(images, verbose=0), reloaded.predict(images, verbose=0))
