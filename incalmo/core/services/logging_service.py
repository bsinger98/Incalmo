import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os

import structlog
import json


class TokenUsageLogger:
    def __init__(self, path: str):
        self._path = path

    def record(
        self,
        *,
        call_type: str,
        model: str,
        step: int,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int,
        cache_creation_tokens: int,
        reasoning_tokens: int,
        response_id: str | None,
    ):
        # input_tokens and output_tokens are LangChain's normalised TOTALS: input_tokens already INCLUDES the
        # cached tokens and output_tokens already includes the reasoning tokens. The three detail counts break
        # those totals down, they do not add to them - never sum a detail onto its total.
        #
        # Without cache_read/cache_creation a run's cost is not computable, only bounded. Every call resends
        # the whole conversation, so input_tokens grows monotonically and the same prefix is billed on each
        # call - at the full input rate if it missed cache, at ~10-20% of it if it hit. Measured across our
        # corpus that is a 5x spread between the two bounds ($586 vs $116), so the split is the number.
        #
        # response_id is the provider's own id for this call: the join key back to their billing records, so
        # cost can be reconciled against ground truth instead of trusted as our own arithmetic.
        with open(self._path, "a") as f:   # one row per LLM call, written immediately
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "call_type": call_type,
                "model": model,
                "step": step,
                "response_id": response_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_read_tokens": cache_read_tokens,
                "cache_creation_tokens": cache_creation_tokens,
                "reasoning_tokens": reasoning_tokens,
            }) + "\n")


class IncalmoLogger:
    def __init__(self, operation_id: str):
        output_dir_override = os.environ.get("INCALMO_OUTPUT_DIR")
        if output_dir_override:
            self.logger_dir_path = output_dir_override
        else:
            self.logger_dir_path = f"output/{operation_id}"
            if not os.path.exists("output"):
                os.mkdir("output")

        os.makedirs(self.logger_dir_path, exist_ok=True)

        self._configure_file_only_logging()

    def create_logger_dir(self, operation_id: str):
        # Create timestamp log directory
        self.logger_dir_path = f"output/{operation_id}"

        if not os.path.exists("output"):
            os.mkdir("output")

        if not os.path.exists(f"output/{operation_id}"):
            os.mkdir(f"output/{operation_id}")

        self._configure_file_only_logging()

    def _configure_file_only_logging(self):
        """Configure specific loggers to only write to files, not console"""

        loggers_to_suppress = [
            "llm",
            "actions_logger",
        ]

        for logger_name in loggers_to_suppress:
            logger = logging.getLogger(logger_name)
            logger.propagate = (
                False  # Don't propagate to root logger (which goes to console)
            )

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
        logger.propagate = False

        return logger

    def token_usage_logger(self) -> TokenUsageLogger:
        return TokenUsageLogger(f"{self.logger_dir_path}/token_usage.json")

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
        stdlib_logger.propagate = False

        return logger
