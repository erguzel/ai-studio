"""Detect malaria in blood smear images with architectures that are declared.

Three architectures are compared in a single run: a small CNN, the same CNN
behind augmentation layers, and a classifier grown on top of VGG16. None of
them is written as code - each is a dict of layer, compile and fit specs in
CONFIG, resolved at run time by aistudio.model.keras_utils. Adding a fourth is
an edit to CONFIG.

Because augmentation is a layer in keras 3 rather than a generator wrapped
around the training loop, and because a transfer model differs from a plain one
only by naming a base, all three run through the same few lines below.

The images are split into train, validation and test by file name, once, with
the seed CONFIG declares - so the score at the end comes from images no model
was trained on and no early stopping ever looked at.

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
from pathlib import Path

import matplotlib
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report

from aistudio.model.keras_utils import build_model, fit_params, true_and_predicted
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
        'validation_split': 0.15,
        'test_split': 0.15,
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
            'base_model': {'module': 'tensorflow.keras.applications', 'object': 'VGG16',
                           'hyper_params': {'weights': 'imagenet', 'include_top': False,
                                            'input_shape': (64, 64, 3)}},
            'base_layer': 'block3_pool',
            # the pretrained weights are kept as they are: training them at the
            # rate the new head needs is what destroys them
            'base_trainable': False,
            # VGG16 wants BGR with the ImageNet means removed, not 0-1 pixels
            'input_layers': [{'module': 'preprocessing', 'object': 'VGGPreprocessing'}],
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


IMAGE_SUFFIXES = ('.png', '.jpg', '.jpeg')


def split_files(config: dict):
    """Cuts the image files into fixed train, validation and test lists.

    The split is made over the file names, not over the stream of images keras
    would hand out: a dataset reshuffles on every pass, so slicing one gives a
    different set of images each time it is read, and a test set that leaks
    into validation. Splitting the names once, with a declared seed, gives
    three sets that are disjoint by construction and identical on every run.

    The cut is made class by class, so each set carries the same class balance
    as the whole.

    Args:
        config (dict): the initialize block of CONFIG.

    Returns:
        tuple: the class names, and three (paths, labels) pairs.
    """
    source = Path(config['source'])
    class_names = sorted(d.name for d in source.iterdir() if d.is_dir())

    rng = np.random.default_rng(config['seed'])
    parts = ([], [], [])

    # each class is cut by the same fractions, so every set keeps the balance
    # of the whole - which a single cut across a shuffled list only gets right
    # on average
    for index, name in enumerate(class_names):
        files = sorted(str(path) for path in (source / name).iterdir()
                       if path.suffix.lower() in IMAGE_SUFFIXES)
        files = np.array(files)[rng.permutation(len(files))]

        validation_size = int(len(files) * config['validation_split'])
        test_size = int(len(files) * config['test_split'])
        train_end = len(files) - validation_size - test_size
        validation_end = train_end + validation_size

        for part, chunk in zip(parts, (files[:train_end],
                                       files[train_end:validation_end],
                                       files[validation_end:]), strict=True):
            part.append((chunk, np.full(len(chunk), index)))

    splits = []
    for part in parts:
        paths = np.concatenate([chunk for chunk, _ in part])
        labels = np.concatenate([chunk for _, chunk in part])
        order = rng.permutation(len(paths))
        splits.append((paths[order], labels[order]))

    return class_names, tuple(splits)


def as_dataset(paths, labels, config: dict, class_count: int, shuffle: bool):
    """Builds a batched dataset out of one list of image files.

    Args:
        paths: the image files.
        labels: their class indices.
        config (dict): the initialize block of CONFIG.
        class_count (int): number of classes, for the one hot labels.
        shuffle (bool): shuffle between epochs, which only training wants.

    Returns:
        The dataset.
    """
    size = tuple(config['image_size'])

    def load(path, label):
        image = tf.io.decode_image(tf.io.read_file(path), channels=3, expand_animations=False)
        return tf.image.resize(image, size), label

    dataset = tf.data.Dataset.from_tensor_slices(
        (paths, tf.keras.utils.to_categorical(labels, class_count)))
    if shuffle:
        dataset = dataset.shuffle(len(paths), seed=config['seed'])
    return (dataset
            .map(load, num_parallel_calls=tf.data.AUTOTUNE)
            .batch(config['batch_size'])
            .prefetch(tf.data.AUTOTUNE))


def load_data(config: dict, limit_batches: int | None = None):
    """Reads the image folders into train, validation and test datasets.

    Args:
        config (dict): the initialize block of CONFIG.
        limit_batches (int, optional): keep only this many batches of each
            dataset, for a quick run.

    Returns:
        tuple: the three datasets, the class names, and the three set sizes.
    """
    class_names, splits = split_files(config)
    train, validation, test = (
        as_dataset(paths, labels, config, len(class_names), shuffle=shuffle)
        for (paths, labels), shuffle in zip(splits, (True, False, False), strict=True)
    )

    if limit_batches:
        train, validation, test = (d.take(limit_batches) for d in (train, validation, test))

    sizes = {name: len(paths) for name, (paths, _) in
             zip(('train', 'validation', 'test'), splits, strict=True)}
    return train, validation, test, class_names, sizes


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
    train, validation, test, class_names, sizes = load_data(
        config['initialize'], limit_batches)

    report = JSNode(
        title=title,
        config=config,
        class_names=class_names,
        train_images=sizes['train'],
        validation_images=sizes['validation'],
        test_images=sizes['test'],
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
