import logging
import tempfile
from typing import Any

from flores.logger import FloresLogger


def test_logger_stderr(capsys: Any) -> None:
    """Test the Flores logger on stderr.

    We expect the logger to use stderr by default, and to use color in the log messages.
    """
    logger = FloresLogger("test_logger", logging.DEBUG)

    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    captured = capsys.readouterr()

    assert captured.out == ""
    for message_type in ("debug", "info", "warning", "error", "critical"):
        assert (
            f"{message_type} message" in captured.err
        ), f"{message_type} message not in stderr."
    # If the reset color command exists, that means there is color.
    assert "\x1b[0m" in captured.err, "No color found in stderr."


def test_logger_stderr_no_color(capsys) -> None:
    """Test the Flores logger on stderr without color.

    We expect the logger to use stderr by default, and to not use color if we specify
    so.
    """
    logger = FloresLogger("test_logger", logging.DEBUG, no_color=True)

    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    captured = capsys.readouterr()

    assert captured.out == ""
    for message_type in ("debug", "info", "warning", "error", "critical"):
        assert (
            f"{message_type} message" in captured.err
        ), f"{message_type} message not in stderr."
    # If the reset color command exists, that means there is color.
    assert "\x1b[0m" not in captured.err, "Color found in stderr."


def test_logger_file() -> None:
    """Test the Flores logger on a log file.

    We expect the logger to write logs to a log file if we specify so, and to use color
    in the log messages.
    """
    with tempfile.NamedTemporaryFile() as log_file:
        logger = FloresLogger("test_logger", logging.DEBUG, log_file=log_file.name)

        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

        with open(log_file.name, "r") as file:
            log_data = file.read()

        for message_type in ("debug", "info", "warning", "error", "critical"):
            assert (
                f"{message_type} message" in log_data
            ), f"{message_type} message not in log file."
        # If the reset color command exists, that means there is color.
        assert "\x1b[0m" in log_data, "No color found in log file."
