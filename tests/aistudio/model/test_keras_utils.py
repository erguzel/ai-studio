"""Keras helper tests; skipped unless the tf extra is installed."""
import pytest

tf = pytest.importorskip('tensorflow', reason='needs the tf extra')

import numpy as np  # noqa: E402 - only reached when tensorflow is there

from aistudio.model.keras_utils import (  # noqa: E402
    build_model,
    build_sequential_model,
    build_transfer_model,
    fit_params,
    true_and_predicted,
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


def transfer_spec(**overrides):
    """A VGG16 head, with weights=None so no 58 MB download is needed."""
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
    spec.update(overrides)
    return spec


def trunk_of(model):
    """The pretrained part, which sits in the model as one nested model."""
    return next(layer for layer in model.layers if isinstance(layer, tf.keras.Model))


def test_transfer_models_continue_the_named_layer():
    model = build_transfer_model(transfer_spec())

    names = [layer.name for layer in trunk_of(model).layers]
    assert 'block3_pool' in names
    assert 'block4_conv1' not in names  # the rest of VGG16 is left behind
    assert model.output_shape == (None, 2)


def test_the_pretrained_base_is_frozen_by_default():
    """Training it at the rate a fresh head needs is what destroys it."""
    model = build_transfer_model(transfer_spec())

    assert trunk_of(model).trainable is False

    trunk_weights = {id(weight) for weight in trunk_of(model).weights}
    assert model.trainable_weights  # the head still learns
    assert not any(id(weight) in trunk_weights for weight in model.trainable_weights)


def test_the_pretrained_base_can_be_unfrozen():
    model = build_transfer_model(transfer_spec(base_trainable=True))

    assert trunk_of(model).trainable is True
    trunk_weights = {id(w) for w in trunk_of(model).weights}
    assert any(id(w) in trunk_weights for w in model.trainable_weights)


def test_input_layers_run_before_the_pretrained_base():
    model = build_transfer_model(transfer_spec(input_layers=[
        {'module': 'tensorflow.keras.layers', 'object': 'Rescaling',
         'hyper_params': {'scale': 1.0 / 255}},
    ]))

    kinds = [type(layer).__name__ for layer in model.layers]
    assert kinds.index('Rescaling') < kinds.index(type(trunk_of(model)).__name__)


def test_a_transfer_model_trains(dataset):
    images, labels = dataset
    model = build_transfer_model(transfer_spec(base_model={
        'module': 'tensorflow.keras.applications', 'object': 'VGG16',
        'hyper_params': {'weights': None, 'include_top': False, 'input_shape': (32, 32, 3)}}))

    padded = np.pad(images, ((0, 0), (12, 12), (12, 12), (0, 0)))
    history = model.fit(padded, labels, epochs=1, batch_size=8, verbose=0)

    assert 'loss' in history.history


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


class BrightnessModel:
    """A model that is right about every image, by construction.

    It reads the image rather than a learned weight, so any disagreement
    between its guesses and the labels can only come from the pairing.
    """

    def __call__(self, inputs, training=False):
        bright = np.mean(np.asarray(inputs), axis=(1, 2, 3)) > 0.5
        return np.stack([~bright, bright], axis=1).astype('float32')


def reshuffling_dataset(size: int = 64, batch: int = 8):
    """A dataset that hands out its elements in a different order every pass."""
    values = np.repeat([0.2, 0.8], size // 2).astype('float32')
    images = values.reshape(-1, 1, 1, 1) * np.ones((size, 4, 4, 3), dtype='float32')
    labels = tf.keras.utils.to_categorical((values > 0.5).astype(int), 2)

    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    return dataset.shuffle(size, seed=0, reshuffle_each_iteration=True).batch(batch)


def test_the_dataset_this_is_tested_against_really_does_reshuffle():
    dataset = reshuffling_dataset()

    first = np.concatenate([np.argmax(labels, axis=1) for _, labels in dataset])
    second = np.concatenate([np.argmax(labels, axis=1) for _, labels in dataset])

    assert not np.array_equal(first, second)


def test_predictions_are_paired_with_their_own_labels():
    """Two passes over a shuffled dataset would score this perfect model at chance."""
    true, predicted = true_and_predicted(BrightnessModel(), reshuffling_dataset())

    assert np.array_equal(true, predicted)


def test_true_and_predicted_cover_the_whole_dataset():
    true, predicted = true_and_predicted(BrightnessModel(), reshuffling_dataset(size=64))

    assert len(true) == 64
    assert len(predicted) == 64
