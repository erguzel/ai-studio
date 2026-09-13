"""Renders a run report as markdown, beside the report.json of the same run.

report.json stays the machine readable record; this module turns the same
JSNode into something a person reads without running anything - which is what
makes a committed sample run worth looking at.
"""
import json
import shutil
from pathlib import Path

from aistudio.serialization.report import jsonize

FIGURE_DIR = 'figures'


def as_data(report) -> dict:
    """Turns a JSNode - or anything jsonize handles - into plain data.

    Going through jsonize is deliberate: the markdown and the json of a run are
    then rendered from the very same structure, numpy scalars included.

    Args:
        report: a JSNode, or any structure jsonize can serialize.

    Returns:
        dict: the report as plain python data.
    """
    return json.loads(jsonize(report, verbose=False))


def is_table(value) -> bool:
    """Tells whether a value is better shown as a table than as json.

    A table is a mapping of names to records that all carry the same scalar
    fields - a per class metrics report is one. A mapping whose entries have
    nothing in common, such as a pipeline configuration, is not, and is better
    left as json.

    Args:
        value: anything.

    Returns:
        bool: True if the value renders as a table.
    """
    if not isinstance(value, dict):
        return False

    rows = [v for v in value.values() if isinstance(v, dict)]
    if len(rows) < 2:
        return False
    if any(row.keys() != rows[0].keys() for row in rows):
        return False
    return not any(isinstance(cell, (dict, list)) for row in rows for cell in row.values())


def as_heading(key: str) -> str:
    """Turns a report key into a section heading.

    Args:
        key (str): the key as the run declared it.

    Returns:
        str: the heading text.
    """
    return key.replace('_', ' ').capitalize()


def render_table(name: str, value: dict) -> list[str]:
    """Renders a dict of dicts as a markdown table.

    Entries whose value is not a dict - an overall accuracy sitting next to the
    per class rows, say - are listed under the table instead of distorting it.

    Args:
        name (str): heading for the section.
        value (dict): the mapping to render.

    Returns:
        list[str]: markdown lines.
    """
    rows = {k: v for k, v in value.items() if isinstance(v, dict)}
    columns = list(dict.fromkeys(c for row in rows.values() for c in row))
    # a column of whole numbers is a count, and reads better without decimals
    whole = {c: all(is_whole(row.get(c)) for row in rows.values()) for c in columns}

    lines = [f'## {as_heading(name)}', '']
    lines.append('| | ' + ' | '.join(columns) + ' |')
    lines.append('| --- | ' + ' | '.join('---' for _ in columns) + ' |')
    for key, row in rows.items():
        cells = [format_value(row.get(c, ''), whole=whole[c]) for c in columns]
        lines.append(f'| {key} | ' + ' | '.join(cells) + ' |')

    loose = {k: v for k, v in value.items() if not isinstance(v, dict)}
    if loose:
        lines.append('')
        lines.extend(f'- {k}: {format_value(v)}' for k, v in loose.items())
    lines.append('')
    return lines


def is_whole(value) -> bool:
    """Tells whether a value is a number without a fractional part.

    Args:
        value: anything.

    Returns:
        bool: True for ints and for floats such as the 8.0 that json gives back
            for a count of 8.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and value.is_integer()


def format_value(value, whole: bool = False) -> str:
    """Formats a leaf value for a markdown cell.

    Args:
        value: a scalar or a list of scalars.
        whole (bool, optional): render a number without decimals, for a column
            that holds counts.

    Returns:
        str: the value, with floats rounded to four decimals and lists joined.
    """
    if whole and is_whole(value):
        return str(int(value))
    if isinstance(value, float):
        return f'{value:.4f}'
    if isinstance(value, list):
        return ', '.join(format_value(v) for v in value)
    return str(value)


def save_figures(figures: dict, directory: Path) -> list[str]:
    """Writes the run's figures next to the report and links them.

    Args:
        figures (dict): caption to figure. A figure is either an object
            exposing ``savefig(path)`` - a matplotlib figure, say - or the path
            of an image already on disk, which is copied.
        directory (Path): the run directory.

    Returns:
        list[str]: markdown lines, empty when there are no figures.
    """
    if not figures:
        return []

    target = directory / FIGURE_DIR
    target.mkdir(parents=True, exist_ok=True)

    lines = ['## Figures', '']
    for caption, figure in figures.items():
        name = caption.lower().replace(' ', '-') + '.png'
        if hasattr(figure, 'savefig'):
            figure.savefig(target / name, bbox_inches='tight')
        else:
            shutil.copyfile(figure, target / name)
        lines.extend([f'### {caption}', '', f'![{caption}]({FIGURE_DIR}/{name})', ''])
    return lines


def write_run_report(report, directory, figures: dict | None = None,
                     filename: str = 'report.md') -> str:
    """Writes the markdown report of one run.

    Scalars become a summary table, mappings of named records become tables of
    their own, and anything deeper - the declared pipeline above all - is kept
    verbatim as json in a collapsed block, so the report stays readable without
    hiding what actually ran.

    Args:
        report: the run's JSNode.
        directory: the run directory, usually what persist_ml_model returned.
        figures (dict, optional): caption to figure, as save_figures takes them.
        filename (str, optional): name to write under. Defaults to report.md.

    Returns:
        str: the path of the report that was written.
    """
    data = as_data(report)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    title = data.pop('title', directory.name)
    lines = [f'# {title}', '']

    summary = {k: v for k, v in data.items() if not isinstance(v, dict)}
    if summary:
        lines.extend(['## Summary', '', '| field | value |', '| --- | --- |'])
        lines.extend(f'| {k} | {format_value(v)} |' for k, v in summary.items())
        lines.append('')

    for key, value in data.items():
        if is_table(value):
            lines.extend(render_table(key, value))

    lines.extend(save_figures(figures or {}, directory))

    verbatim = {k: v for k, v in data.items() if isinstance(v, dict) and not is_table(v)}
    for key, value in verbatim.items():
        lines.extend([
            f'## {as_heading(key)}', '',
            '<details><summary>as declared</summary>', '',
            '```json',
            json.dumps(value, indent=2),
            '```', '',
            '</details>', '',
        ])

    path = directory / filename
    path.write_text('\n'.join(lines))
    return str(path)
