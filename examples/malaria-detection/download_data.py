"""Download the malaria cell images this example classifies.

The archive is not kept in the repository: it is 337 MB of thin blood smear
images published by the Lister Hill National Center for Biomedical
Communications, U.S. National Library of Medicine.

    S. Rajaraman et al., "Pre-trained convolutional neural networks as feature
    extractors toward improved malaria parasite detection in thin blood smear
    images", PeerJ 6:e4568, 2018.
    https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/image-processing/malaria-datasheet.html

Usage:
    python download_data.py                 # extracts into data/raw
    python download_data.py --target /tmp/x --url <mirror>
"""
import argparse
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ARCHIVE_URL = 'https://data.lhncbc.nlm.nih.gov/public/Malaria/cell_images.zip'
EXPECTED_CLASSES = ('Parasitized', 'Uninfected')
EXPECTED_IMAGES = 27558


def download(url: str, target: Path) -> None:
    """Streams the archive to a temporary file and extracts it.

    It is streamed rather than read into memory because the archive is 337 MB.

    Args:
        url (str): archive to fetch.
        target (Path): directory to extract into.
    """
    print(f'downloading {url}')
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix='.zip') as archive:
        with urllib.request.urlopen(url) as response:
            shutil.copyfileobj(response, archive)
        archive.flush()
        with zipfile.ZipFile(archive.name) as zf:
            zf.extractall(target)


def find_corpus(target: Path) -> Path:
    """Locates the folder holding the class folders.

    The archive is expected to hold a single ``cell_images`` folder, but it is
    found by looking for the class folders rather than by name, so a repackaged
    archive still works.

    Args:
        target (Path): directory the archive was extracted into.

    Returns:
        Path: the corpus root.

    Raises:
        RuntimeError: if no folder holds both class folders.
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
    """Counts the images and warns when the count is not the published one.

    Args:
        corpus (Path): the corpus root.

    Returns:
        int: the number of images found.
    """
    images = sum(1 for _ in corpus.glob('*/*.png'))
    if images != EXPECTED_IMAGES:
        print(f'warning: expected {EXPECTED_IMAGES} images, found {images}', file=sys.stderr)
    return images


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download the malaria cell images used by this example.')
    parser.add_argument('--target', default=Path('data/raw'), type=Path,
                        help='directory to extract into (default: data/raw)')
    parser.add_argument('--url', default=ARCHIVE_URL,
                        help=f'archive to download (default: {ARCHIVE_URL})')
    args = parser.parse_args()

    download(args.url, args.target)
    corpus = find_corpus(args.target)
    images = verify(corpus)
    print(f'{images} images in {len(EXPECTED_CLASSES)} classes under {corpus}')
