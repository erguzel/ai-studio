import json
from pathlib import Path

import joblib

from aistudio.model.model_utils import create_run_dir, persist_ml_model, save_model
from aistudio.serialization.report import JSNode


class EstimatorWithASaveField:
    """An estimator that happens to carry a save attribute that is not a method."""

    save = 'not a method'


class SelfSavingModel:
    """Stands in for a keras model, which persists itself through save()."""

    def __init__(self):
        self.saved_to = None

    def save(self, path):
        self.saved_to = path
        Path(path).write_text('a model in its own format')


def test_save_model_lets_a_model_save_itself(tmp_path):
    model = SelfSavingModel()

    save_model(model, str(tmp_path / 'model.keras'))

    assert model.saved_to == str(tmp_path / 'model.keras')
    assert (tmp_path / 'model.keras').read_text() == 'a model in its own format'


def test_save_model_pickles_anything_else(tmp_path):
    save_model({'coefficients': [1, 2, 3]}, str(tmp_path / 'model.sav'))

    assert joblib.load(tmp_path / 'model.sav') == {'coefficients': [1, 2, 3]}


def test_save_model_ignores_a_save_attribute_that_is_not_callable(tmp_path):
    save_model(EstimatorWithASaveField(), str(tmp_path / 'model.sav'))

    assert isinstance(joblib.load(tmp_path / 'model.sav'), EstimatorWithASaveField)


def test_persist_ml_model_saves_a_self_saving_model(tmp_path):
    model = SelfSavingModel()

    run_dir = persist_ml_model('BaseModel.keras', model, 'run_pipeline.py', str(tmp_path))

    assert (Path(run_dir) / 'BaseModel.keras').exists()
    assert model.saved_to == str(Path(run_dir) / 'BaseModel.keras')


def test_persist_ml_model_writes_the_report_beside_it(tmp_path):
    run_dir = persist_ml_model(
        'model.sav', {'a': 1}, 'run_pipeline.py', str(tmp_path),
        mainReport=JSNode(document_count=60),
    )

    report = json.loads((Path(run_dir) / 'report.json').read_text())
    assert report == {'document_count': 60}


def test_persist_ml_model_gives_every_run_its_own_folder(tmp_path):
    runs = {persist_ml_model('m.sav', {}, 'run_pipeline.py', str(tmp_path)) for _ in range(3)}

    assert len(runs) == 3


def test_create_run_dir_makes_a_fresh_folder_per_run(tmp_path):
    runs = {create_run_dir('run_pipeline.py', str(tmp_path)) for _ in range(3)}

    assert len(runs) == 3
    assert all(Path(run).is_dir() for run in runs)


def test_create_run_dir_puts_the_run_under_the_title(tmp_path):
    run = Path(create_run_dir('run_pipeline.py', str(tmp_path)))

    assert run.parent == tmp_path / 'models' / 'run_pipeline.py'


def test_several_models_can_share_one_run(tmp_path):
    """A run comparing architectures keeps them together under one report."""
    run_dir = persist_ml_model(
        'BaseModel.keras', SelfSavingModel(), 'run_pipeline.py', str(tmp_path),
        mainReport=JSNode(models={'BaseModel': {'accuracy': 0.9}}),
    )

    again = persist_ml_model(
        'Transfer.keras', SelfSavingModel(), 'run_pipeline.py', runDir=run_dir,
        mainReport=JSNode(models={'BaseModel': {'accuracy': 0.9},
                                  'Transfer': {'accuracy': 0.95}}),
    )

    assert again == run_dir
    assert (Path(run_dir) / 'BaseModel.keras').exists()
    assert (Path(run_dir) / 'Transfer.keras').exists()


def test_the_report_of_a_shared_run_describes_every_model(tmp_path):
    run_dir = persist_ml_model('a.sav', {}, 'run_pipeline.py', str(tmp_path),
                               mainReport=JSNode(models={'a': {'accuracy': 0.9}}))
    persist_ml_model('b.sav', {}, 'run_pipeline.py', runDir=run_dir,
                     mainReport=JSNode(models={'a': {'accuracy': 0.9},
                                               'b': {'accuracy': 0.95}}))

    report = json.loads((Path(run_dir) / 'report.json').read_text())
    assert sorted(report['models']) == ['a', 'b']
