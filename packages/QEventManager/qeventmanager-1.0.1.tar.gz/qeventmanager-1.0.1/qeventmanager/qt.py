# coding: utf-8
QtExist = False
QtVersion = None
QtList = [
    'PyQt5',
    'PySide2',
    'PySide6',
    'PyQt6',
]
for qt in QtList:
    try:
        __import__(qt)
        QtExist = True
        QtVersion = qt
        break
    except ImportError:
        pass
if not QtExist:
    raise ImportError('No Qt library found. Please install one of the following libraries: {}'.format(QtList))

if QtVersion == 'PyQt5':
    from PyQt5.QtCore import QThreadPool, QThread, pyqtSignal as Signal, pyqtProperty as Property, QObject, \
        PYQT_VERSION_STR as __version__
elif QtVersion == 'PySide2':
    from PySide2.QtCore import QThreadPool, QThread, Signal, Property, QObject
    from PySide2 import __version__
elif QtVersion == 'PySide6':
    from PySide6.QtCore import QThreadPool, QThread, Signal, Property, QObject
    from PySide6 import __version__
elif QtVersion == 'PyQt6':
    from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal as Signal, pyqtProperty as Property, QObject, \
        PYQT_VERSION_STR as __version__
else:
    raise ImportError('No Qt library found. Please install one of the following libraries: {}'.format(QtList))

print('Using Qt library: {} version: {}'.format(QtVersion, __version__))
