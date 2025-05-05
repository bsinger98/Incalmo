import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os


class PerryLogger:
    def __init__(self, operation_id: str):
        # Create timestamp log directory
        self.logger_dir_path = f"logs/{operation_id}"

        if not os.path.exists("logs"):
            os.mkdir("logs")

        if not os.path.exists(f"logs/{operation_id}"):
            os.mkdir(f"logs/{operation_id}")

    def setup_logger(self, logger_name: str):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        logger_handler = RotatingFileHandler(
            f"{self.logger_dir_path}/{logger_name}.log", maxBytes=5 * 1024 * 1024
        )
        logger_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
        logger_handler.setFormatter(logger_formatter)
        logger_handler.setLevel(logging.DEBUG)

        logger.handlers.clear()
        logger.addHandler(logger_handler)

        return logger


### Legacy logging setup
plugin_logger = logging.getLogger("deception-plugin")
plugin_logger.setLevel(logging.DEBUG)


def init_logger(path: str):
    if not os.path.exists("logs"):
        os.mkdir("logs")

    log_path = os.path.join(path, "internal.log")

    plugin_logger_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024)
    plugin_logger_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
    plugin_logger_handler.setFormatter(plugin_logger_formatter)
    plugin_logger_handler.setLevel(logging.DEBUG)

    plugin_logger.handlers.clear()
    plugin_logger.addHandler(plugin_logger_handler)


def get_logger():
    return plugin_logger


def log_event(event: str, message: str):
    plugin_logger.debug(f"{event:<24}\t{message}")


def log_trusted_agents(trusted_agents):
    for agent in trusted_agents:
        log_event(
            "TRUSTED AGENT",
            f"{agent.paw} ({agent.host} - {agent.host_ip_addrs})",
        )
