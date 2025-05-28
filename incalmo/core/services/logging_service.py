import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os

import structlog
import json


class PerryLogger:
    def __init__(self, operation_id: str):
        # Create timestamp log directory
        self.logger_dir_path = f"output/{operation_id}"

        if not os.path.exists("output"):
            os.mkdir("output")

        if not os.path.exists(f"output/{operation_id}"):
            os.mkdir(f"output/{operation_id}")

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

    def action_logger(self):
        actions_log_path = f"{self.logger_dir_path}/actions.json"

        structlog.configure(
            processors=[structlog.processors.JSONRenderer()],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        logger = structlog.get_logger("actions_logger")

        file_handler = RotatingFileHandler(
            actions_log_path, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        stdlib_logger = logging.getLogger("actions_logger")
        stdlib_logger.setLevel(logging.DEBUG)
        stdlib_logger.handlers.clear()
        stdlib_logger.addHandler(file_handler)

        return logger
