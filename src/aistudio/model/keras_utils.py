"""Builds keras models out of declared specs, the way the examples declare them.

Importing this module needs the tf extra: ``pip install ai-studio[tf]``. Nothing
else in the package imports tensorflow.

A model is a dict, not code. ``layers`` is a list of specs, ``compile`` holds
the arguments of keras' compile - optimizers and callbacks being specs of their
own, resolved however deeply they nest - and ``base_model`` names a pretrained
model to build on top of. That is the whole vocabulary::

    {
        'layers': [
            {'module': 'tensorflow.keras.layers', 'object': 'Conv2D',
             'hyper_params': {'filters': 32, 'kernel_size': 2}},
            {'module': 'tensorflow.keras.layers', 'object': 'Flatten'},
        ],
        'compile': {
            'loss': 'binary_crossentropy',
            'optimizer': {'module': 'tensorflow.keras.optimizers',
                          'object': 'Adam', 'hyper_params': {'learning_rate': 0.001}},
            'metrics': ['accuracy'],
        },
    }
"""
import numpy as np
import tensorflow as tf

from aistudio.data.meta.module_utils import instantiate


def build_sequential_model(spec: dict, compile_model: bool = True):
    """Stacks the declared layers into a Sequential model.

    Args:
        spec (dict): the model spec. ``layers`` is required, ``compile`` is
            applied when present.
        compile_model (bool, optional): compile the model with the declared
            arguments. Defaults to True.

    Returns:
        The keras model.
    """
    model = tf.keras.models.Sequential(instantiate(spec['layers']))
    return compile_declared(model, spec) if compile_model else model


def build_transfer_model(spec: dict, compile_model: bool = True):
    """Continues a pretrained model with the declared layers.

    The pretrained model is instantiated from ``base_model``, and the declared
    layers are chained onto the output of the layer named by ``base_layer`` -
    so which part of the pretrained model is reused is itself declared.

    Args:
        spec (dict): the model spec, carrying ``base_model``, ``base_layer``
            and ``layers``.
        compile_model (bool, optional): compile the model with the declared
            arguments. Defaults to True.

    Returns:
        The keras model.
    """
    base = instantiate(spec['base_model'])
    outputs = base.get_layer(spec['base_layer']).output
    for layer in instantiate(spec['layers']):
        outputs = layer(outputs)

    model = tf.keras.Model(base.input, outputs)
    return compile_declared(model, spec) if compile_model else model


def build_model(spec: dict, compile_model: bool = True):
    """Builds whichever kind of model the spec describes.

    A spec naming a ``base_model`` continues that model; any other spec stacks
    its layers from scratch.

    Args:
        spec (dict): the model spec.
        compile_model (bool, optional): compile the model with the declared
            arguments. Defaults to True.

    Returns:
        The keras model.
    """
    if 'base_model' in spec:
        return build_transfer_model(spec, compile_model=compile_model)
    return build_sequential_model(spec, compile_model=compile_model)


def compile_declared(model, spec: dict):
    """Compiles a model with the arguments the spec declares.

    Args:
        model: the keras model.
        spec (dict): the model spec. Without a ``compile`` key the model is
            returned uncompiled.

    Returns:
        The same model.
    """
    if 'compile' in spec:
        model.compile(**instantiate(spec['compile']))
    return model


def fit_params(spec: dict) -> dict:
    """Turns the declared fit arguments into the objects keras expects.

    Callbacks are specs like any other, so they arrive as instances rather than
    as descriptions of instances.

    Args:
        spec (dict): the model spec.

    Returns:
        dict: the keyword arguments to hand to ``model.fit``.
    """
    return instantiate(spec.get('fit', {}))


def true_and_predicted(model, dataset):
    """Runs a model over a dataset and returns the labels next to its guesses.

    Both come out of the same pass over the dataset, batch by batch, because a
    dataset need not hand out its elements in the same order twice - keras
    shuffles by default, and reshuffles on every iteration. Collecting the
    labels in one pass and the predictions in another would pair each
    prediction with some other image's label, and score any model at chance.

    The model is called rather than asked to predict, which is what a manual
    loop wants: predict builds a compiled function per batch shape, and warns
    about retracing once the last, shorter batch arrives.

    Args:
        model: a trained keras model.
        dataset: a batched dataset of inputs and one hot labels.

    Returns:
        tuple: two arrays of class indices, the true ones and the predicted.
    """
    true, predicted = [], []
    for inputs, labels in dataset:
        true.append(np.argmax(labels, axis=1))
        predicted.append(np.argmax(np.asarray(model(inputs, training=False)), axis=1))
    return np.concatenate(true), np.concatenate(predicted)
