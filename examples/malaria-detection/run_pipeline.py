"""Detect malaria in blood smear images with architectures that are declared.

Three architectures are compared in a single run: a small CNN, the same CNN
behind augmentation layers, and a classifier grown on top of VGG16. None of
them is written as code - each is a dict of layer, compile and fit specs in
CONFIG, resolved at run time by aistudio.model.keras_utils. Adding a fourth is
an edit to CONFIG.

Because augmentation is a layer in keras 3 rather than a generator wrapped
around the training loop, and because a transfer model differs from a plain one
only by naming a base, all three run through the same few lines below.

The run writes one report covering every architecture: report.json for
machines, report.md with the confusion matrices and training curves for people,
and each trained model beside them.

Before running, fetch the images:

    python download_data.py

Then, from this directory:

    python run_pipeline.py                  # the full comparison
    python run_pipeline.py --limit-batches 4 --epochs 1     # a quick look
"""
import argparse
import os

import matplotlib
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report

from aistudio.model.keras_utils import build_model, fit_params
from aistudio.model.model_utils import persist_ml_model
from aistudio.serialization.report import JSNode
from aistudio.serialization.run_report import write_run_report

matplotlib.use('Agg')  # the run writes figures to disk, it never opens a window
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

LAYERS = 'tensorflow.keras.layers'

RESCALE = {'module': LAYERS, 'object': 'Rescaling', 'hyper_params': {'scale': 1.0 / 255}}

AUGMENTATION = [
    {'module': LAYERS, 'object': 'RandomFlip', 'hyper_params': {'mode': 'horizontal_and_vertical'}},
    {'module': LAYERS, 'object': 'RandomRotation', 'hyper_params': {'factor': 0.2}},
    {'module': LAYERS, 'object': 'RandomZoom', 'hyper_params': {'height_factor': 0.1}},
]

CONVOLUTIONS = [
    {'module': LAYERS, 'object': 'Conv2D',
     'hyper_params': {'filters': 32, 'kernel_size': 2, 'padding': 'same', 'activation': 'relu'}},
    {'module': LAYERS, 'object': 'MaxPooling2D', 'hyper_params': {'pool_size': 2}},
    {'module': LAYERS, 'object': 'Dropout', 'hyper_params': {'rate': 0.2}},
    {'module': LAYERS, 'object': 'Conv2D',
     'hyper_params': {'filters': 64, 'kernel_size': 2, 'padding': 'same', 'activation': 'relu'}},
    {'module': LAYERS, 'object': 'MaxPooling2D', 'hyper_params': {'pool_size': 2}},
    {'module': LAYERS, 'object': 'Dropout', 'hyper_params': {'rate': 0.2}},
    {'module': LAYERS, 'object': 'Flatten'},
    {'module': LAYERS, 'object': 'Dense', 'hyper_params': {'units': 512, 'activation': 'relu'}},
    {'module': LAYERS, 'object': 'Dropout', 'hyper_params': {'rate': 0.4}},
    {'module': LAYERS, 'object': 'Dense', 'hyper_params': {'units': 2, 'activation': 'softmax'}},
]

COMPILE = {
    'loss': 'categorical_crossentropy',
    'optimizer': {'module': 'tensorflow.keras.optimizers', 'object': 'Adam',
                  'hyper_params': {'learning_rate': 0.001}},
    'metrics': ['accuracy'],
}

FIT = {
    'epochs': 20,
    'verbose': 2,
    'callbacks': [
        {'module': 'tensorflow.keras.callbacks', 'object': 'EarlyStopping',
         'hyper_params': {'monitor': 'val_loss', 'patience': 4,
                          'restore_best_weights': True}},
    ],
}

CONFIG = {
    'initialize': {
        'source': os.path.join(HERE, 'data', 'raw', 'cell_images'),
        'image_size': (64, 64),
        'batch_size': 32,
        # a third is held out, then halved into validation and test
        'holdout_split': 0.3,
        'seed': 35,
    },
    'models': {
        'BaseModel': {
            'layers': [RESCALE, *CONVOLUTIONS],
            'compile': COMPILE,
            'fit': FIT,
        },
        'Augmented': {
            'layers': [RESCALE, *AUGMENTATION, *CONVOLUTIONS],
            'compile': COMPILE,
            'fit': FIT,
        },
        'VGG16Transfer': {
            # VGG16 was trained on unscaled pixels, so this one gets no Rescaling
            'base_model': {'module': 'tensorflow.keras.applications', 'object': 'VGG16',
                           'hyper_params': {'weights': 'imagenet', 'include_top': False,
                                            'input_shape': (64, 64, 3)}},
            'base_layer': 'block3_pool',
            'layers': [
                {'module': LAYERS, 'object': 'Flatten'},
                {'module': LAYERS, 'object': 'Dense',
                 'hyper_params': {'units': 256, 'activation': 'relu'}},
                {'module': LAYERS, 'object': 'Dropout', 'hyper_params': {'rate': 0.3}},
                {'module': LAYERS, 'object': 'Dense',
                 'hyper_params': {'units': 2, 'activation': 'softmax'}},
            ],
            'compile': COMPILE,
            'fit': FIT,
        },
    },
}


def load_data(config: dict, limit_batches: int | None = None):
    """Reads the image folders into train, validation and test datasets.

    keras splits a folder in two; the second half is halved again here, so the
    score reported at the end comes from images no model was tuned against.

    Args:
        config (dict): the initialize block of CONFIG.
        limit_batches (int, optional): keep only this many batches of each
            dataset, for a quick run.

    Returns:
        tuple: train, validation and test datasets, plus the class names.
    """
    common = {
        'image_size': config['image_size'],
        'batch_size': config['batch_size'],
        'label_mode': 'categorical',
        'seed': config['seed'],
        'validation_split': config['holdout_split'],
    }
    train = tf.keras.utils.image_dataset_from_directory(
        config['source'], subset='training', **common)
    holdout = tf.keras.utils.image_dataset_from_directory(
        config['source'], subset='validation', **common)

    class_names = list(train.class_names)
    half = holdout.cardinality().numpy() // 2
    validation, test = holdout.take(half), holdout.skip(half)

    if limit_batches:
        train = train.take(limit_batches)
        validation = validation.take(limit_batches)
        test = test.take(limit_batches)

    return train, validation, test, class_names


def true_and_predicted(model, dataset):
    """Runs the model over a dataset and returns the labels next to its guesses.

    Args:
        model: a trained keras model.
        dataset: a batched dataset of images and one hot labels.

    Returns:
        tuple: two arrays of class indices, the true ones and the predicted.
    """
    true = np.concatenate([np.argmax(labels, axis=1) for _, labels in dataset])
    predicted = np.argmax(model.predict(dataset, verbose=0), axis=1)
    return true, predicted


def confusion_figure(true, predicted, class_names, title: str):
    """Draws the confusion matrix of one model.

    Args:
        true: true class indices.
        predicted: predicted class indices.
        class_names (list): names to label the axes with.
        title (str): figure title.

    Returns:
        The matplotlib figure.
    """
    figure, axes = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(
        true, predicted, display_labels=class_names, ax=axes, colorbar=False,
        cmap='Blues')
    axes.set_title(title)
    return figure


def history_figure(history, title: str):
    """Draws accuracy against epoch for the training and validation sets.

    Args:
        history: the History keras returned from fit.
        title (str): figure title.

    Returns:
        The matplotlib figure.
    """
    figure, axes = plt.subplots(figsize=(5, 4))
    epochs = range(1, len(history.history['accuracy']) + 1)
    axes.plot(epochs, history.history['accuracy'], label='train', marker='o')
    axes.plot(epochs, history.history['val_accuracy'], label='validation', marker='o')
    axes.set_xlabel('epoch')
    axes.set_ylabel('accuracy')
    axes.set_title(title)
    axes.legend(loc='lower right')
    return figure


def main(config: dict = CONFIG, limit_batches: int | None = None,
         epochs: int | None = None) -> JSNode:
    """Trains every declared architecture and reports them side by side.

    Args:
        config (dict): the pipeline, as CONFIG declares it.
        limit_batches (int, optional): shorten every dataset, for a quick run.
        epochs (int, optional): override the declared number of epochs.

    Returns:
        JSNode: the run report.
    """
    title = os.path.basename(__file__)
    train, validation, test, class_names = load_data(config['initialize'], limit_batches)

    report = JSNode(
        title=title,
        config=config,
        class_names=class_names,
        train_batches=int(train.cardinality()),
        validation_batches=int(validation.cardinality()),
        test_batches=int(test.cardinality()),
    )
    summary, figures = {}, {}
    run_dir = None

    for name, spec in config['models'].items():
        print(f'--- {name}')
        model = build_model(spec)

        params = fit_params(spec)
        if epochs is not None:
            params['epochs'] = epochs
        history = model.fit(train, validation_data=validation, **params)

        loss, accuracy = model.evaluate(test, verbose=0)
        true, predicted = true_and_predicted(model, test)
        print(classification_report(true, predicted, target_names=class_names))

        summary[name] = {
            'accuracy': float(accuracy),
            'loss': float(loss),
            'parameters': int(model.count_params()),
            'epochs': len(history.history['loss']),
        }
        report.update(models=summary)

        figures[f'{name} confusion matrix'] = confusion_figure(
            true, predicted, class_names, f'{name} - accuracy {accuracy:.4f}')
        figures[f'{name} training history'] = history_figure(history, f'{name} - accuracy')

        run_dir = persist_ml_model(f'{name}.keras', model, title,
                                   runDir=run_dir, mainReport=report)

    write_run_report(report, run_dir, figures=figures)
    for figure in figures.values():
        plt.close(figure)

    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--limit-batches', type=int, default=None,
                        help='keep only this many batches of each dataset')
    parser.add_argument('--epochs', type=int, default=None,
                        help='override the declared number of epochs')
    args = parser.parse_args()

    main(limit_batches=args.limit_batches, epochs=args.epochs)
