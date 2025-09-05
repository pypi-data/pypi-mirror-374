# coding: utf-8
from inspect import signature
from typing import Callable, Union, Any

from PySide6.QtCore import Signal

from .handler import RequestHandler, ResponseHandler
from .logger import logger
from .qt import QObject
from .que_thread import QueThread, QueThreadPool
from .tools import ImageHelper


class QEventManager(QObject):
    failed = Signal(object)
    threadStarted = Signal()
    threadFinished = Signal()
    poolStarted = Signal()
    poolFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.queThread = QueThread(self)
        self.queThreadPool = QueThreadPool(self)
        self.dbSession = None

        self.queThread.result.connect(self._handleResponse)
        self.queThread.failed.connect(self.failed)
        self.queThreadPool.result.connect(self._handleResponse)
        self.queThreadPool.failed.connect(self.failed)

        self.queThreadPool.started.connect(self.poolStarted)
        self.queThreadPool.finished.connect(self.poolFinished)
        self.queThread.started.connect(self.threadStarted)
        self.queThread.finished.connect(self.threadFinished)

    def deleteLater(self):
        self.queThread.deleteLater()
        self.queThreadPool.deleteLater()
        if self.dbSession and hasattr(self.dbSession, 'close'):
            self.dbSession.close()
            self.dbSession = None
        super().deleteLater()

    def setDbSession(self, session: Any = None):
        self.dbSession = session

    def _handleResponse(self, response: ResponseHandler):
        if response.error:
            logger.error(f"task failed: {response.error}")
            return
        try:
            if response.slot:
                result = response.result
                response.slot(result)
        except RuntimeError as e:
            logger.warning(f"slot execution failed: {e}")

    def addTask(self, func: Callable, *args, slot: Callable = None, **kwargs):
        """
        添加任务
        :param func: 
        :param args: 
        :param slot: 
        :param kwargs: 
        :return: 
        """
        request = RequestHandler(func, *args, **kwargs, slot=slot)
        self.queThread.addTask(request)

    def addTaskToPool(self, func: Callable, *args, slot: Callable = None, **kwargs):
        """
        添加任务到线程池
        :param func: 
        :param args: 
        :param slot: 
        :param kwargs: 
        :return: 
        """
        request = RequestHandler(func, *args, **kwargs, slot=slot)
        self.queThreadPool.addTask(request)

    def addSqlTask(self, func: Callable, *args, slot: Callable = None, **kwargs):
        """
        添加数据库任务
        :param func: 
        :param args: 
        :param slot: 
        :param kwargs: 
        :return: 
        """
        if not self.dbSession:
            raise Exception('No database session found')
        params = signature(func).parameters
        if 'session' not in params:
            raise Exception('No session parameter found in function signature')
        kwargs['session'] = self.dbSession
        self.addTask(func, *args, slot=slot, **kwargs)

    def addSqlTaskToPool(self, func: Callable, *args, slot: Callable = None, **kwargs):
        """
        添加数据库任务到线程池
        :param func: 
        :param args: 
        :param slot: 
        :param kwargs: 
        :return: 
        """
        if not self.dbSession:
            raise Exception('No database session found')
        params = signature(func)
        if 'session' not in params:
            raise Exception('No session parameter found in function signature')
        kwargs['session'] = self.dbSession
        self.addTaskToPool(func, *args, slot=slot, **kwargs)

    def addLoadImageFromUrl(self, url: str, slot: Callable, **kwargs):
        """
        从url添加加载图像
        :param url: 
        :param slot:
        :return: 
        """
        func = ImageHelper.get_image_from_url
        args = (url,)
        self.addTaskToPool(func, *args, slot=slot, **kwargs)

    def addDownloadImage(self, url: str, file_path: str, slot: Callable, **kwargs):
        """
        下载图片任务到线程池
        :param url: 
        :param file_path: 
        :param slot: 
        :return: 
        """
        func = ImageHelper.download_image
        args = (url, file_path)
        self.addTaskToPool(func, *args, slot=slot, **kwargs)

    def addLoadImageFromFile(self, file_path: str, slot: Callable, width: int = None, **kwargs):
        """
        从文件加载图片任务到线程池
        :param file_path:     
        :param slot: 
        :param width: 
        :return: 
        """
        func = ImageHelper.get_image_from_file
        args = (file_path,)
        kwargs = {'width': width, **kwargs}
        self.addTaskToPool(func, *args, slot=slot, **kwargs)
