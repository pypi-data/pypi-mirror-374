# coding: utf-8
from logging import getLogger, StreamHandler, Formatter, DEBUG

logger = getLogger('qeventmanager')
handler = StreamHandler()
handler.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(DEBUG)
