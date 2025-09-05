# QEventManager

#### 介绍

QEventManager使用多线程的方式对任务进行处理，qasync的另一个替代

#### 软件架构

依赖于Qt的QThread类，使用多线程的方式对任务进行处理。

#### 安装教程

```
pip install qeventmanager
```

#### 使用说明
[examples](examples)

##### 加载Url图片

```python
# coding: utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from qeventmanager import qevent_manager

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.verticalLayout = QVBoxLayout(self)
        self.pushButton = QPushButton(self)
        self.pushButton.setText("Click me")

        self.label = QLabel(self)
        self.label.setText("Hello, world!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)

        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.label, 1)

        self.pushButton.clicked.connect(self.handle_click)

    def handle_click(self):
        url = 'https://i.loli.net/2018/12/06/5c0867986a2a0.jpg'
        qevent_manager.addLoadImageFromUrl(url, slot=self.handle_image, use_pil=False)

    def handle_image(self, image: QImage):
        image = image.scaledToWidth(self.verticalLayout.geometry().width())
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.resize(1000, 600)
    demo.show()
    sys.exit(app.exec())
```


##### 加载本地图片
```python
# coding: utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from qeventmanager import qevent_manager

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.verticalLayout = QVBoxLayout(self)
        self.pushButton = QPushButton(self)
        self.pushButton.setText("Click me")

        self.label = QLabel(self)
        self.label.setText("Hello, world!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)

        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.label, 1)

        self.pushButton.clicked.connect(self.handle_click)

    def handle_click(self):
        url = './img.jpg'
        qevent_manager.addLoadImageFromFile(url, slot=self.handle_image, use_pil=False)

    def handle_image(self, image: QImage):
        image = image.scaledToWidth(self.verticalLayout.geometry().width())
        self.label.setPixmap(QPixmap.fromImage(image))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.resize(1000, 600)
    demo.show()
    sys.exit(app.exec())
```

##### 加载自定义函数
```python
# coding: utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from requests import Response, post

from qeventmanager import qevent_manager


def baidu():
    url = 'https://wallpaper.soutushenqi.com/timeStamp?product_id=52&version_code=29106&sign=EB9C805D055305DB83FCAFEA541B9714'
    response = post(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.verticalLayout = QVBoxLayout(self)
        self.pushButton = QPushButton(self)
        self.pushButton.setText("Click me")

        self.label = QLabel(self)
        self.label.setText("Hello, world!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)

        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.label, 1)

        self.pushButton.clicked.connect(self.handle_click)

    def handle_click(self):
        qevent_manager.addTask(baidu, slot=self.handle)
        # qevent_manager.addTaskToPool(baidu, slot=self.handle)

    def handle(self, response: Response):
        self.label.setText(response.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.resize(1000, 600)
    demo.show()
    sys.exit(app.exec())
```