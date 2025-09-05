# coding: utf-8
from collections import deque
from traceback import print_exc, format_exc
from inspect import signature

from .handler import RequestHandler, ResponseHandler
from .qt import QThread, QThreadPool, Signal


class QueThread(QThread):
    result = Signal(ResponseHandler)
    failed = Signal(object)
    message = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = deque()

    def handleTask(self, task: RequestHandler):
        func = task.func
        params = signature(func).parameters
        if 'massage' in params:
            task.kwargs['message'] = self.message
        result = func(*task.args, **task.kwargs)
        return result

    def run(self):
        while self.tasks:
            task = self.tasks.popleft()
            try:
                result = self.handleTask(task)
                error = None
            except Exception as e:
                result = None
                error = format_exc()
                print_exc()
                self.failed.emit(error)
            self.result.emit(ResponseHandler(task.slot, result=result, error=error))

    def addTask(self, task: RequestHandler):
        self.tasks.append(task)
        if not self.isRunning():
            self.start()

    def deleteLater(self):
        self.tasks.clear()
        self.terminate()
        super().deleteLater()


class QueThreadPool(QThread):
    result = Signal(ResponseHandler)
    failed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = deque()
        self.pool = QThreadPool()

    def setMaxThreadCount(self, maxThreadCount: int):
        self.pool.setMaxThreadCount(maxThreadCount)

    def run(self):
        while self.tasks:
            task = self.tasks.popleft()
            self.pool.start(lambda: self.handleTask(task))
        self.pool.waitForDone()

    def handleTask(self, task: RequestHandler):
        try:
            result = task.func(*task.args, **task.kwargs)
            error = None
        except Exception as e:
            result = None
            error = str(e)
            print_exc()
            self.failed.emit(error)
        self.result.emit(ResponseHandler(task.slot, result=result, error=error))

    def addTask(self, task: RequestHandler):
        self.tasks.append(task)
        if not self.isRunning():
            self.start()

    def deleteLater(self):
        self.tasks.clear()
        self.pool.clear()
        self.terminate()
        super().deleteLater()
