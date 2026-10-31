import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def clear_process_local_rate_limits():
    # Each TestClient instance shares the in-memory dev limiter just like one worker.
    import app.main as main
    main._rate_buckets.clear()
    yield
    main._rate_buckets.clear()
