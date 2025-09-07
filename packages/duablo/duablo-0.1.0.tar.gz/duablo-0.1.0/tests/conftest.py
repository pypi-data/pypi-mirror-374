import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest


def copy_asset(filename: str, path: Path):
    dest_path = path / filename
    shutil.copy(Path(__file__).with_suffix('').parent / 'assets' / filename, dest_path)

    return dest_path


@pytest.fixture(scope='function')
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)
