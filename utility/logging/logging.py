import logging
from logging.handlers import RotatingFileHandler
import os


class PerryLogger:
    plugin_logger = logging.getLogger("perry")
    caldera_log_file = None

    @staticmethod
    def get_logger():
        return PerryLogger.plugin_logger

    @staticmethod
    def setup_logger(experiment_output_dir: str):
        # Setup perry logging
        log_filename = f"perry_log.log"
        log_path = os.path.join(experiment_output_dir, log_filename)

        PerryLogger.plugin_logger.setLevel(logging.DEBUG)
        plugin_logger_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024)
        plugin_logger_formatter = logging.Formatter(
            "%(asctime)s {%(filename)s:%(lineno)d} %(levelname)s:%(message)s"
        )
        plugin_logger_handler.setFormatter(plugin_logger_formatter)
        plugin_logger_handler.setLevel(logging.DEBUG)

        PerryLogger.plugin_logger.handlers.clear()
        PerryLogger.plugin_logger.addHandler(plugin_logger_handler)

        # Setup caldera logging
        log_filename = f"caldera_log.log"
        log_path = os.path.join(experiment_output_dir, log_filename)
        PerryLogger.caldera_log_file = open(log_path, "w")


### Legacy code ###
def get_logger():
    return PerryLogger.plugin_logger


def log(message: str):
    PerryLogger.plugin_logger.debug(message)


def log_event(event: str, message: str):
    PerryLogger.plugin_logger.debug(f"{event:<24}\t{message}")


def log_trusted_agents(trusted_agents):
    for agent in trusted_agents:
        log_event(
            "TRUSTED AGENT",
            f"{agent.paw} ({agent.host} - {agent.host_ip_addrs})",
        )
