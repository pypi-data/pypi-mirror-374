# coding: utf-8
from typing import Callable, Any, Union

from .qt import QObject, Signal


class RequestHandler:
    def __init__(self, func: Callable, *args, slot: Callable = None, **kwargs):
        self.func = func
        self.slot = slot
        self.args = args
        self.kwargs = kwargs


class ResponseHandler:
    def __init__(self, slot: Callable, result: Any = None, error: Union[Exception, str] = None):
        self.slot = slot
        self.result = result
        if isinstance(error, Exception):
            error = str(error)
        elif error is None:
            error = ""
        self.error = error

    def __str__(self):
        return f"ResponseHandler(slot={self.slot}, result={self.result}, error={self.error})"
