import pytest
from fastapi.testclient import TestClient

from signalroom import main
from signalroom.config import Settings


@pytest.fixture(scope="session")
def api_client(tmp_path_factory):
    runtime = tmp_path_factory.mktemp("signalroom-runtime")
    main.settings = Settings(data_dir=runtime, random_seed=17, account_count=1200)
    with TestClient(main.app) as client:
        yield client
