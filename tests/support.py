import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


@contextmanager
def temporary_directory():
    root = Path(os.environ.get('BRFC_TEST_TMP') or Path(__file__).resolve().parents[1] / '.test-tmp')
    root.mkdir(parents=True, exist_ok=True)
    # Short name: on Windows the full path (repository + .test-tmp + copied trees) must stay under MAX_PATH.
    directory = root / uuid4().hex[:12]
    directory.mkdir()
    try:
        yield str(directory)
    finally:
        shutil.rmtree(directory)
