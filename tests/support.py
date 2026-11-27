import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


@contextmanager
def temporary_directory():
    root = Path(os.environ.get('BRFC_TEST_TMP') or Path(__file__).resolve().parents[1] / '.test-tmp')
    root.mkdir(parents=True, exist_ok=True)
    directory = root / str(uuid4())
    directory.mkdir()
    try:
        yield str(directory)
    finally:
        shutil.rmtree(directory)
