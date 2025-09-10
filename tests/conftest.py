import pytest
from incalmo.core.services.config_service import ConfigService


@pytest.fixture(scope="class")
def incalmo_config():
    return ConfigService().get_config()
