import logging
from contextlib import redirect_stderr, redirect_stdout
from typing import Callable, Optional, Union

from wurlitzer import pipes

# From https://stackoverflow.com/a/66209331
class LoggerWriter:
    """Writer allowing redirection of streams to logger methods."""

    def __init__(self, writer: Callable):
        self._writer = writer
        self._msg = ""

    def write(self, message: str):
        self._msg = self._msg + message
        while "\n" in self._msg:
            pos = self._msg.find("\n")
            self._writer(self._msg[:pos])
            self._msg = self._msg[pos + 1 :]

    def flush(self):
        if self._msg != "":
            self._writer(self._msg)
            self._msg = ""


class redirect_output:
    """Context manager to redirect stdout and stderr to logger."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # Current Python process redirects
        self.redirect_stdout = redirect_stdout(LoggerWriter(self.logger.info))
        self.redirect_stderr = redirect_stderr(LoggerWriter(self.logger.warning))
        # This redirects stdout/stderr from C libraries and child processes (joblib)
        self.c_redirect = pipes(
            stdout=LoggerWriter(self.logger.info),
            stderr=LoggerWriter(self.logger.warning),
        )

    def __enter__(self):
        self.redirect_stdout.__enter__()
        self.redirect_stderr.__enter__()
        if self.c_redirect:
            self.c_redirect.__enter__()

    def __exit__(self, *args, **kwargs):
        if self.c_redirect:
            self.c_redirect.__exit__(*args, **kwargs)
        self.redirect_stderr.__exit__(*args, **kwargs)
        self.redirect_stdout.__exit__(*args, **kwargs)
