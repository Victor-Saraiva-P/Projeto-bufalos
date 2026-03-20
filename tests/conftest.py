import pytest

from mock_config import MockDataConfig


@pytest.fixture(scope="session")
def mock_data_config() -> MockDataConfig:
    return MockDataConfig()
