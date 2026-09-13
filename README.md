# ai-studio

[![CI](https://github.com/erguzel/ai-studio/actions/workflows/ci.yml/badge.svg)](https://github.com/erguzel/ai-studio/actions/workflows/ci.yml)

A small kit for running machine learning experiments in which the pipeline is
data rather than code. Every step — the cleaners, the vectorizer, the layers,
the optimizer, the callbacks — is named in a config dict and resolved at run
time. Swapping a model is an edit to that dict, not to the code.

It is a kit for *how* a run is declared, measured and recorded. It is not a
collection of state-of-the-art models: the ones in the examples are
deliberately ordinary. Squeezing the last points of accuracy out of a model is
a data scientist's job, and a different one.

## The idea

An object is named by its module and its name, with the arguments it is built
from. Specs nest, so the optimizer inside a compile block and the callbacks
inside a fit block are resolved too:

```python
CONFIG = {
    'execute': {
        'model_instance': {
            'module': 'sklearn.ensemble',
            'object': 'RandomForestClassifier',
            'hyper_params': {'n_estimators': 500, 'random_state': 0},
        },
    },
}
```

Two verbs turn that into objects. `resolve_spec` hands back what a spec names,
for the functions and constants a pipeline applies itself. `instantiate` builds
it, with its own arguments built first. Nothing is guessed: the caller says
which it wants.

Because the config is a plain dict, it is also the thing the run reports. Every
run writes the exact pipeline it executed into `report.json`, next to its
metrics.

## Install

Python 3.11 or newer. The package is not on PyPI; install it from a clone:

```bash
git clone https://github.com/erguzel/ai-studio.git
cd ai-studio
pip install -e .
```

Optional extras: `.[dev]` for pytest and ruff, `.[tf]` for the keras helpers.

## Examples

Each example is self-contained: a `download_data.py` that fetches its corpus, a
`run_pipeline.py` that declares the pipeline in `CONFIG`, and a `sample-run/`
holding the report of one real run, so you can see the output without running
anything.

| example | what it shows | sample run |
| --- | --- | --- |
| [bbc-news-classification](examples/bbc-news-classification) | text: cleaning, stemming, TF-IDF, a random forest over 5 classes | [report](examples/bbc-news-classification/sample-run/report.md) |
| [malaria-detection](examples/malaria-detection) | images: three keras architectures compared in one run, including transfer learning | [report](examples/malaria-detection/sample-run/report.md) |

Those runs recorded 0.957 accuracy over 2,225 news articles, and 0.950 / 0.955 /
0.922 for the three malaria architectures over 27,558 cell images. They are
there as examples of what a run records, not as results worth chasing.

## Running an example

From the example's own directory — the pinned requirements refer to the package
by a relative path, which pip resolves against the working directory:

```bash
cd examples/bbc-news-classification
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Fetch the corpus, then run:

```bash
python download_data.py
python run_pipeline.py
```

The malaria example downloads 337 MB and trains three models, so try it small
first:

```bash
python run_pipeline.py --limit-batches 4 --epochs 1
```

## What a run produces

Each run gets its own directory, and runs never overwrite each other:

```
models/run_pipeline.py/_13-Sep-2026_23_36_53/
├── BaseModel.keras          the trained model, in whatever format it owns
├── report.json              the pipeline as declared, plus the metrics
├── report.md                the same run, for a person to read
└── figures/                 confusion matrices, training curves
```

`report.json` is what you compare runs with. `report.md` is what you open.

## Scope

**Try your own parameters.** Change `CONFIG` and run again. Swap the
classifier, add a layer, move a hyper-parameter. The code under `CONFIG` stays
as it is, and each run writes a report you can hold next to the last one.

**On issues and pull requests.** This repository is here to be read, run and
forked, not maintained as a library. I do not review pull requests regularly.
Please fork it and make it yours.

## Development

```bash
uv run --extra dev pytest        # uv does not install extras on its own
uv run --extra dev ruff check .
```

The keras tests skip themselves unless the `tf` extra is installed. CI runs the
suite on Python 3.11, 3.12 and 3.13, resolves each example's pinned stack on
the lowest of those, and runs the keras tests with tensorflow installed.

## Notes

**GPU.** Nothing here pins a device, so keras uses a GPU if TensorFlow finds
one. On Linux with NVIDIA that means installing `tensorflow[and-cuda]` instead
of `tensorflow`; the plain package is CPU-only. macOS has no working GPU path
on current TensorFlow, and results are not bit-identical across devices anyway.

**No nltk.** The text example uses `snowballstemmer` and scikit-learn's stop
word list. nltk would have worked, but it carries a long stream of advisories
for code this repository never calls, and it wants a corpus download at run
time — which also means the example would not run offline.

## Data

The example corpora are not kept in this repository; each `download_data.py`
fetches its own from the original source.

The BBC news corpus comes from University College Dublin (D. Greene and
P. Cunningham, ICML 2006). All rights in the article text remain with the BBC.

The malaria cell images come from the Lister Hill National Center for
Biomedical Communications, U.S. National Library of Medicine (S. Rajaraman et
al., *PeerJ* 6:e4568, 2018).

## Licence

MIT — see [LICENSE.txt](LICENSE.txt).
