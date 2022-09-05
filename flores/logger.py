"""The logging functionality for Flores."""

import logging
from typing import Any, Optional, Union


class FloresLogFormatter(logging.Formatter):
    """Implement a custom log formatter for Flores."""

    def __init__(self, no_color: bool = False) -> None:
        """Initialize the Flores log formatter.

        :param no_color: if True, do not use colors in the logs.
        """
        super().__init__()
        self.__no_color = no_color

    @property
    def colors(self) -> dict[str, str]:
        """Return a mapping of color names to terminal color commands."""
        return {
            "magenta_bold": "\x1b[35;1m",
            "magenta": "\x1b[35;20m",
            "white_bold": "\x1b[37;1m",
            "white_dim": "\x1b[37;2m",
            "yellow_bold": "\x1b[33;1m",
            "red": "\x1b[31;20m",
            "red_bold": "\x1b[31;1m",
            "reset": "\x1b[0m",
        }

    def __color_text(self, text: str, color: str) -> str:
        """Color some text with a given color.

        If the log formatter has been configured to be colorless, then the text will not
        be colored.

        :param text: the text to color.
        :param color: the color to use (see `self.colors`).
        :ret: the colored text.
        """
        if self.__no_color:
            return text
        return self.colors[color] + text + self.colors["reset"]

    def __get_format(self, log_level: Union[int, str]) -> str:
        """Get a log format given a log level.

        :param log_level: the level of logging
            (i.e. `logging.DEBUG|INFO|WARNING|ERROR|CRITICAL`).
        :ret: the appropriate format.
        """
        if log_level == logging.DEBUG:
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + self.__color_text("[DEBUG] %(message)s", "white_dim")
            )
        elif log_level == logging.INFO:
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + self.__color_text("%(message)s", "white_bold")
            )

        elif log_level == logging.WARNING:
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + self.__color_text("[WARNING] %(message)s", "yellow_bold")
            )
        elif log_level == logging.ERROR:
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + self.__color_text("[ERROR (noncritical)] %(message)s", "red")
            )

        elif log_level == logging.CRITICAL:
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + self.__color_text("[ERROR] %(message)s", "red_bold")
            )
        else:  # pragma: no cover
            # Technically we should never reach this case.
            fmt = (
                self.__color_text("flores ", "magenta_bold")
                + self.__color_text("(%(name)s) ", "magenta")
                + "[???] %(message)s"
            )

        return fmt

    # This method is shadowing a Python builtin as per A003, but it's also what we need
    # to overwrite for the formatter; thus we have to ignore A003 here.
    def format(self, record: Any) -> str:  # noqa: A003
        """Format a log record.

        :param record: the log record to format.
        :ret: a formatted log record.
        """
        log_fmt = self.__get_format(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FloresLogger:
    """Implement a custom logger for Flores."""

    def __init__(
        self,
        name: str,
        log_level: Union[int, str] = logging.INFO,
        log_file: Optional[str] = None,
        no_color: bool = False,
    ) -> None:
        """Initialize a Flores logger.

        :param name: the name of the logger.
        :param log_level: the level of logging
            (i.e. `logging.DEBUG|INFO|WARNING|ERROR|CRITICAL`).
        :param log_file: a file to write the logs to (optionally); if None, the logs
            will be written in stderr.
        :param no_color: if True, no colors are used in the logs.
        """
        self.__logger = logging.getLogger(name)
        self.__log_handler: Optional[logging.Handler] = None
        self.set_level(log_level)
        self.set_log_file(log_file)
        self.set_color(not no_color)

    def set_level(self, log_level: Union[int, str]) -> None:
        """Set a logging level for the logger.

        :param log_level: the level of logging
            (i.e. `logging.DEBUG|INFO|WARNING|ERROR|CRITICAL`).
        """
        self.__logger.setLevel(log_level)

    def set_log_file(self, log_file: Optional[str]) -> None:
        """Specify a log file for the logger.

        :param log_file: a file to write the logs to (optionally); if None, the logs
            will be written in stderr.
        """
        # Make sure to remove the handler first to avoid having duplicate handlers.
        if self.__logger.hasHandlers() and self.__log_handler is not None:
            self.__logger.removeHandler(self.__log_handler)

        if log_file is None:
            self.__log_handler = logging.StreamHandler()
        else:
            self.__log_handler = logging.FileHandler(log_file)

        # MyPy needs this for some reason, as it is not sure that the log handler has
        # been correctly initialized at this point.
        assert isinstance(self.__log_handler, logging.Handler)
        # This must be set to the lowest level, as we want the handler to send all
        # messages to the destination.
        self.__log_handler.setLevel(logging.DEBUG)
        self.__logger.addHandler(self.__log_handler)

    def set_color(self, use_color: bool = True) -> None:
        """Specify whether or not to use color in the logs.

        :param use_color: if True, use color in the logs.
        """
        if self.__logger.hasHandlers() and self.__log_handler is not None:
            self.__log_handler.setFormatter(FloresLogFormatter(no_color=not use_color))

    def debug(self, message: str) -> None:
        """Emit a debug log message.

        :param message: the log message to emit.
        """
        self.__logger.debug(message)

    def info(self, message: str) -> None:
        """Emit an info log message.

        :param message: the log message to emit.
        """
        self.__logger.info(message)

    def warning(self, message: str) -> None:
        """Emit a warning log message.

        :param message: the log message to emit.
        """
        self.__logger.warning(message)

    def error(self, message: str) -> None:
        """Emit an error log message.

        :param message: the log message to emit.
        """
        self.__logger.error(message)

    def critical(self, message: str) -> None:
        """Emit a critical log message.

        :param message: the log message to emit.
        """
        self.__logger.critical(message)
