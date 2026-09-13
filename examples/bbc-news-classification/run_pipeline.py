"""Classify BBC news articles with a pipeline that is declared, not hard coded.

Every step of the pipeline - the cleaners, the stemmer, the vectorizer, the
model - is named in CONFIG as a module and object pair, and resolved at run time
by aistudio.data.meta.module_utils. Swapping the model or the vectorizer is an
edit to CONFIG, not to the code below.

The run is summarised in a JSNode report, written next to the trained model as
report.json for machines and report.md - with the confusion matrix - for
people.

Before running, fetch the corpus:

    python download_data.py

Then, from this directory:

    python run_pipeline.py
"""
import os
from pathlib import Path

import matplotlib
import numpy as np
from sklearn.datasets import load_files
from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.model_selection import train_test_split

from aistudio.data.meta.module_utils import instantiate, resolve_spec
from aistudio.model.model_utils import persist_ml_model
from aistudio.serialization.report import JSNode
from aistudio.serialization.run_report import write_run_report

matplotlib.use('Agg')  # the run writes figures to disk, it never opens a window
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

CONFIG = {
    'initialize': {
        'source': str(HERE / 'data' / 'raw' / 'bbc'),
        'extension': '.txt',
        'type': 'text-document',
    },
    'cleanse': {
        'char_cleaner_function': {
            'module': 'aistudio.data.text_utils',
            'object': 'clear_default_chars',
        },
        'stemming_lemmatization_function': {
            'module': 'aistudio.data.text_utils',
            'object': 'stemming_lematization',
        },
        'stemmer_or_lemmatizer_instance': {
            'module': 'snowballstemmer',
            'object': 'stemmer',
            'hyper_params': {'lang': 'english'},
        },
    },
    'prepare': {
        'vectorizer_instance': {
            'module': 'sklearn.feature_extraction.text',
            'object': 'CountVectorizer',
            'hyper_params': {'max_features': 1500, 'min_df': 5, 'max_df': 0.7},
            'stop_words': {
                'module': 'sklearn.feature_extraction.text',
                'object': 'ENGLISH_STOP_WORDS',
            },
        },
        'transformer_instance': {
            'module': 'sklearn.feature_extraction.text',
            'object': 'TfidfTransformer',
        },
        'test_size': 0.2,
        'random_state': 0,
    },
    'execute': {
        'model_instance': {
            'module': 'sklearn.ensemble',
            'object': 'RandomForestClassifier',
            'hyper_params': {'n_estimators': 500, 'random_state': 0},
        },
    },
}


def main(config: dict = CONFIG) -> JSNode:
    report = JSNode(title=os.path.basename(__file__), config=config)

    # initialize
    corpus = load_files(config['initialize']['source'])
    X, y = np.array(corpus.data), np.array(corpus.target)
    target_names = list(corpus.target_names)
    report.update(document_count=len(X), target_names=target_names)

    # cleanse
    cleanse = config['cleanse']
    docs = resolve_spec(cleanse['char_cleaner_function'])(data=X)
    stemmer = instantiate(cleanse['stemmer_or_lemmatizer_instance'])
    docs = resolve_spec(cleanse['stemming_lemmatization_function'])(
        stem_or_lemmatizer=stemmer, data=docs)

    # prepare
    prepare = config['prepare']
    vectorizer_spec = prepare['vectorizer_instance']
    stop_words = sorted(resolve_spec(vectorizer_spec['stop_words']))
    vectorizer = resolve_spec(vectorizer_spec)(**vectorizer_spec['hyper_params'],
                                               stop_words=stop_words)
    counts = vectorizer.fit_transform(docs).toarray()
    transformed = instantiate(prepare['transformer_instance']).fit_transform(counts).toarray()

    X_train, X_test, y_train, y_test = train_test_split(
        transformed, y,
        test_size=prepare['test_size'], random_state=prepare['random_state'])
    report.update(train_size=len(X_train), test_size=len(X_test),
                  feature_count=transformed.shape[1])

    # execute
    model_spec = config['execute']['model_instance']
    model = instantiate(model_spec)
    model.fit(X_train, y_train)

    # report
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=target_names))
    report.update(metrics=classification_report(
        y_test, y_pred, target_names=target_names, output_dict=True))

    model_name = model_spec['object'] + '.sav'
    run_dir = persist_ml_model(modelName=model_name, trainedModel=model,
                               runTitle=report.get_property('title'), mainReport=report)

    figure, axes = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, display_labels=target_names, ax=axes, colorbar=False,
        cmap='Blues', xticks_rotation=45)
    axes.set_title('{} - accuracy {:.4f}'.format(
        model_spec['object'], report.get_property('metrics')['accuracy']))
    write_run_report(report, run_dir, figures={'Confusion matrix': figure})
    plt.close(figure)

    return report


if __name__ == '__main__':
    main()
