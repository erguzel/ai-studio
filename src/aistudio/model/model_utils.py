from aistudio.exception.exception_utils import Reporter,InterruptPatcher
from joblib import dump 
from pathlib import Path
from os import path,getcwd
from datetime import datetime
import os


def persist_ml_model(modelName:str,trainedModel,runTitle:str,resultDir:str=None,mainReport:Reporter=None):
    """persists a trained ML model to the disk

    Args:
        modelName (str): name of the model
        trainedModel (_type_): trained model object
        main_report (ReportObject): Report object associated with the model train process
        file (str): the main file of execution to use as the name of the output folder
    """
    try:
        current_datetime  = datetime.now().strftime("_%d-%b-%Y_%H_%M_%S")
        model_dir = path.join(getcwd() if resultDir== None else resultDir,'models',os.path.basename(runTitle),current_datetime)
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        model_full_name = path.join(model_dir,modelName)
        dump(trainedModel,model_full_name)
        report_full_name = path.join(model_dir,'report.json')
        if(mainReport!=None):
            with open(report_full_name, 'w') as f:
                f.write(mainReport.reportize())
    except Exception as e:
        InterruptPatcher('persist_model failed',e,log=True,throw=True).act()