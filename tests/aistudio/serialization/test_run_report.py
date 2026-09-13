import json
from pathlib import Path

import pytest

from aistudio.serialization.report import JSNode
from aistudio.serialization.run_report import (
    as_heading,
    format_value,
    is_table,
    is_whole,
    write_run_report,
)

METRICS = {
    'sport': {'precision': 1.0, 'recall': 0.5, 'f1-score': 0.667, 'support': 7},
    'tech': {'precision': 0.8, 'recall': 1.0, 'f1-score': 0.889, 'support': 5},
    'accuracy': 0.9,
}

CONFIG = {
    'initialize': {'source': 'data/raw', 'extension': '.txt'},
    'execute': {'model_instance': {'module': 'sklearn.ensemble', 'object': 'RF'}},
}


def make_report():
    return JSNode(
        title='run_pipeline.py',
        document_count=60,
        target_names=['sport', 'tech'],
        metrics=METRICS,
        config=CONFIG,
    )


class FakeFigure:
    """Stands in for a matplotlib figure, which is known by its savefig."""

    def savefig(self, path, **kwargs):
        Path(path).write_bytes(b'not really a png')


def test_is_table_accepts_records_sharing_their_fields():
    assert is_table(METRICS)


def test_is_table_rejects_a_configuration():
    assert not is_table(CONFIG)


def test_is_table_rejects_scalars_and_single_records():
    assert not is_table('metrics')
    assert not is_table({'only': {'precision': 1.0}})


def test_format_value_rounds_floats_and_joins_lists():
    assert format_value(0.666666) == '0.6667'
    assert format_value(8.0) == '8.0000'
    assert format_value(8.0, whole=True) == '8'
    assert format_value(['sport', 'tech']) == 'sport, tech'
    assert format_value(7) == '7'


def test_is_whole_spots_counts_that_json_made_floats():
    assert is_whole(8) and is_whole(8.0)
    assert not is_whole(0.5)
    assert not is_whole(True)


def test_report_opens_with_the_run_title(tmp_path):
    text = Path(write_run_report(make_report(), tmp_path)).read_text()

    assert text.startswith('# run_pipeline.py')


def test_scalars_become_the_summary_table(tmp_path):
    text = Path(write_run_report(make_report(), tmp_path)).read_text()

    assert '| document_count | 60 |' in text
    assert '| target_names | sport, tech |' in text


def test_metrics_become_a_table_with_the_odd_one_out_beneath(tmp_path):
    text = Path(write_run_report(make_report(), tmp_path)).read_text()

    assert '| | precision | recall | f1-score | support |' in text
    assert '| sport | 1.0000 | 0.5000 | 0.6670 | 7 |' in text
    assert '- accuracy: 0.9000' in text


def test_keys_become_readable_headings():
    assert as_heading('metrics') == 'Metrics'
    assert as_heading('per_class_metrics') == 'Per class metrics'


def test_sections_are_titled_after_their_key(tmp_path):
    text = Path(write_run_report(make_report(), tmp_path)).read_text()

    assert '## Metrics' in text
    assert '## Config' in text


def test_the_configuration_is_kept_verbatim(tmp_path):
    text = Path(write_run_report(make_report(), tmp_path)).read_text()

    assert '<details><summary>as declared</summary>' in text
    assert json.dumps(CONFIG, indent=2) in text


def test_figures_are_written_and_linked(tmp_path):
    write_run_report(make_report(), tmp_path, figures={'Confusion matrix': FakeFigure()})

    assert (tmp_path / 'figures' / 'confusion-matrix.png').exists()
    text = (tmp_path / 'report.md').read_text()
    assert '![Confusion matrix](figures/confusion-matrix.png)' in text


def test_figures_given_as_paths_are_copied(tmp_path):
    source = tmp_path / 'source.png'
    source.write_bytes(b'not really a png')

    write_run_report(make_report(), tmp_path, figures={'Training history': str(source)})

    assert (tmp_path / 'figures' / 'training-history.png').read_bytes() == b'not really a png'


def test_a_report_without_figures_has_no_figure_section(tmp_path):
    assert '## Figures' not in Path(write_run_report(make_report(), tmp_path)).read_text()


def test_the_written_path_is_returned(tmp_path):
    assert write_run_report(make_report(), tmp_path) == str(tmp_path / 'report.md')


def test_missing_title_falls_back_to_the_run_folder(tmp_path):
    text = Path(write_run_report(JSNode(document_count=1), tmp_path)).read_text()

    assert text.startswith(f'# {tmp_path.name}')


@pytest.mark.parametrize('name', ['report.md', 'run.md'])
def test_the_filename_can_be_chosen(tmp_path, name):
    assert (tmp_path / name).exists() is False
    write_run_report(make_report(), tmp_path, filename=name)
    assert (tmp_path / name).exists()
