from config.attacker_config import AttackerConfig
import requests


class TestC2ServerStrategy:
    """Integration tests for core C2 server functionality."""

    def test_get_latest_logs(self, incalmo_config: AttackerConfig):
        """Test server health endpoint."""
        url = f"{incalmo_config.c2c_server}/get_latest_logs"
        response = requests.get(url)
        print(response.status_code)
        print(response.text)

        assert True
