"""Download the BBC news dataset this example classifies.

The corpus is not kept in the repository: the article text is BBC content, so
each user fetches it from the original source at University College Dublin.

    D. Greene and P. Cunningham, "Practical Solutions to the Problem of
    Diagonal Dominance in Kernel Document Clustering", Proc. ICML 2006.
    http://mlg.ucd.ie/datasets/bbc.html

All rights in the article text remain with the BBC.

Usage:
    python download_data.py                 # extracts into data/raw
    python download_data.py --target /tmp/x --url <mirror>
"""
import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

ARCHIVE_URL = 'http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip'
EXPECTED_CLASSES = ('business', 'entertainment', 'politics', 'sport', 'tech')
EXPECTED_DOCUMENTS = 2225


def download(url: str, target: Path) -> None:
    print(f'downloading {url}')
    with urllib.request.urlopen(url) as response:
        archive = response.read()
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        zf.extractall(target)


def find_corpus(target: Path) -> Path:
    """Locates the extracted corpus root: the folder holding the class folders.

    The archive is expected to contain a single top level folder, but it is
    located by looking for the class folders rather than by name, so a
    repackaged archive still works.
    """
    candidates = [target, *(p for p in target.rglob('*') if p.is_dir())]
    for candidate in candidates:
        if all((candidate / c).is_dir() for c in EXPECTED_CLASSES):
            return candidate
    raise RuntimeError(
        f'no folder under {target} holds all of {EXPECTED_CLASSES}; '
        f'found {sorted(p.name for p in target.iterdir())}'
    )


def verify(corpus: Path) -> int:
    documents = sum(1 for _ in corpus.glob('*/*.txt'))
    if documents != EXPECTED_DOCUMENTS:
        print(f'warning: expected {EXPECTED_DOCUMENTS} documents, found {documents}',
              file=sys.stderr)
    return documents


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download the BBC news dataset used by this example.')
    parser.add_argument('--target', default=Path('data/raw'), type=Path,
                        help='directory to extract into (default: data/raw)')
    parser.add_argument('--url', default=ARCHIVE_URL,
                        help=f'archive to download (default: {ARCHIVE_URL})')
    args = parser.parse_args()

    download(args.url, args.target)
    corpus = find_corpus(args.target)
    documents = verify(corpus)
    print(f'{documents} documents in {len(EXPECTED_CLASSES)} classes under {corpus}')
