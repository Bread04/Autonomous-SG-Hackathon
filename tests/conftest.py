import shutil
from pathlib import Path

import pytest

from saf.inputs import RAW_DIR


@pytest.fixture
def raw_copy(tmp_path: Path) -> Path:
    """A writable copy of data/raw, for tests that corrupt an input."""
    return Path(shutil.copytree(RAW_DIR, tmp_path / "raw"))
