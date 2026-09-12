import os
from datetime import datetime
from pathlib import Path

from joblib import dump

from aistudio.common.log import logger
from aistudio.serialization.report import JSNode


def persist_ml_model(modelName:str,trainedModel,runTitle:str,resultDir:str=None,mainReport:JSNode=None):
    """Persists a trained ML model to the disk, next to its run report.

    The model is written to
    ``<resultDir>/models/<runTitle>/<timestamp>/<modelName>`` and, when a
    report is given, ``report.json`` is written beside it.

    Args:
        modelName (str): file name to store the model under.
        trainedModel: the trained model object, persisted with joblib.
        runTitle (str): the executing file, used to name the output folder.
        resultDir (str, optional): root to write under. Defaults to the
            current working directory.
        mainReport (JSNode, optional): report describing the run.

    Returns:
        str: the directory the model and report were written to.
    """
    current_datetime = datetime.now().strftime("_%d-%b-%Y_%H_%M_%S")
    model_dir = os.path.join(
        os.getcwd() if resultDir is None else resultDir,
        'models', os.path.basename(runTitle), current_datetime,
    )
    Path(model_dir).mkdir(parents=True, exist_ok=True)

    dump(trainedModel, os.path.join(model_dir, modelName))

    if mainReport is not None:
        with open(os.path.join(model_dir, 'report.json'), 'w') as f:
            f.write(mainReport.toJson(verbose=False))

    logger.info('persisted model {} to {}', modelName, model_dir)
    return model_dir
