from config.attacker_config import AttackerConfig
import requests


class TestC2ServerStrategy:
    """Integration tests for core C2 server functionality."""

    def test_strategy_status(self, incalmo_config: AttackerConfig):
        """Test server health endpoint."""
        url = f"{incalmo_config.c2c_server}/strategy_status/123"
        response = requests.get(url)

        print(response.text)

        if "not found" in response.text.lower():
            assert True
        else:
            assert False

    def test_strategy_startup(self, incalmo_config: AttackerConfig):
        """Test strategy startup endpoint."""
        id = "test-strategy-startup"
        incalmo_config.id = id
        url = f"{incalmo_config.c2c_server}/startup"
        response = requests.post(url, json=incalmo_config.model_dump())

        print(response.text)
        assert response.status_code == 200

        # Wait a second
        # Check if the strategy is running
        url = f"{incalmo_config.c2c_server}/strategy_status/{id}"
        response = requests.get(url)
        print(response.text)
        assert response.status_code == 200
        assert response.json()["state"] == "running"
        assert response.json()["strategy"] == incalmo_config.name
        assert response.json()["task_id"] == id
        assert response.json()["info"]["status"] == "running"
        assert response.json()["info"]["message"] == "Task is currently running"
