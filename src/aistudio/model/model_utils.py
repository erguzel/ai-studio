import os
from datetime import datetime
from pathlib import Path

from joblib import dump

from aistudio.common.log import logger
from aistudio.serialization.report import JSNode


def save_model(trainedModel, path: str) -> None:
    """Writes a trained model to the given path, in whatever format it owns.

    Frameworks that carry their own serialization - keras above all, whose
    graphs and weights do not survive a pickle - expose a ``save(path)``. Those
    are saved through it, and everything else, sklearn estimators included, is
    pickled with joblib.

    Args:
        trainedModel: the trained model object.
        path (str): file to write to.
    """
    saver = getattr(trainedModel, 'save', None)
    if callable(saver):
        saver(path)
    else:
        dump(trainedModel, path)


def create_run_dir(runTitle:str, resultDir:str|None=None) -> str:
    """Creates the directory one run writes everything into.

    The directory is ``<resultDir>/models/<runTitle>/<timestamp>`` and is
    always freshly created; runs landing on the same timestamp get a ``-2``,
    ``-3``, ... suffix, so no run can overwrite another's results.

    Args:
        runTitle (str): the executing file, used to name the output folder.
        resultDir (str, optional): root to write under. Defaults to the
            current working directory.

    Returns:
        str: the directory that was created.
    """
    run_root = os.path.join(
        os.getcwd() if resultDir is None else resultDir,
        'models', os.path.basename(runTitle),
    )
    stamp = datetime.now().strftime("_%d-%b-%Y_%H_%M_%S")

    attempt = 0
    while True:
        suffix = '' if attempt == 0 else f'-{attempt + 1}'
        model_dir = os.path.join(run_root, stamp + suffix)
        try:
            Path(model_dir).mkdir(parents=True, exist_ok=False)
            return model_dir
        except FileExistsError:
            attempt += 1


def persist_ml_model(
    modelName:str,
    trainedModel,
    runTitle:str,
    resultDir:str|None=None,
    mainReport:JSNode|None=None,
    runDir:str|None=None,
):
    """Persists a trained ML model to the disk, next to its run report.

    The model is written to
    ``<resultDir>/models/<runTitle>/<timestamp>/<modelName>`` and, when a
    report is given, ``report.json`` is written beside it.

    A run that trains several models - one per architecture being compared -
    passes the directory the first call returned back in as ``runDir``, so all
    of them land in the same run with one report describing the lot. The report
    is rewritten on every call, which also means a run that dies half way
    through still leaves what it had reached.

    Args:
        modelName (str): file name to store the model under. Give it the
            extension the model's own format expects - ``.keras`` for a keras
            model, say.
        trainedModel: the trained model object. A model that knows how to
            persist itself, as keras models do, is saved through its own
            ``save(path)``; anything else is pickled with joblib.
        runTitle (str): the executing file, used to name the output folder.
        resultDir (str, optional): root to write under. Defaults to the
            current working directory.
        mainReport (JSNode, optional): report describing the run.
        runDir (str, optional): an existing run directory to write into,
            instead of creating one. runTitle and resultDir are then unused.

    Returns:
        str: the directory the model and report were written to.
    """
    model_dir = create_run_dir(runTitle, resultDir) if runDir is None else runDir

    save_model(trainedModel, os.path.join(model_dir, modelName))

    if mainReport is not None:
        with open(os.path.join(model_dir, 'report.json'), 'w') as f:
            f.write(mainReport.toJson(verbose=False))

    logger.info('persisted model {} to {}', modelName, model_dir)
    return model_dir
