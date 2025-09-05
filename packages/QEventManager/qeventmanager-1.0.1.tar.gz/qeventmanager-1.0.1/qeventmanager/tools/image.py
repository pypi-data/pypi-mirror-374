# coding: utf-8
from io import BytesIO

import requests
from PIL import Image
from PIL.ImageQt import toqimage
from PySide6.QtGui import QImage
from requests import get

requests.packages.urllib3.disable_warnings()


class ImageHelper:
    """
    这个类用于处理图片相关的操作
    """

    @staticmethod
    def get_image_from_url(url: str, **kwargs) -> QImage:
        """
        从url获取图片
        :param url: 图片的url
        :param width: 图片的宽度
        :param use_pil: 是否使用pil库进行图片处理
        :param kwargs: 其他参数
        :return: 图片的二进制数据
        """
        width = kwargs.pop('width', None)
        use_pil = kwargs.pop('use_pil', True)
        response = get(url, verify=False, **kwargs)
        response.raise_for_status()
        if use_pil:
            file_bytes = BytesIO(response.content)
            img = Image.open(file_bytes)
            if width:
                h = int(width / img.width * img.height)
                img.thumbnail((width, h))
            return toqimage(img)
        else:
            return QImage.fromData(response.content)

    @staticmethod
    def get_image_from_file(file_path: str, width: int = 300, use_pil: bool = True) -> QImage:
        """
        从本地文件获取图片
        :param file_path: 图片的本地路径
        :param width: 图片的宽度
        :param use_pil: 是否使用pil库进行图片处理
        :return: 图片的二进制数据
        """
        if not use_pil:
            return QImage(file_path)
        img = Image.open(file_path)
        if width:
            h = int(width / img.width * img.height)
            img.thumbnail((width, h))
        return toqimage(img)

    @staticmethod
    def download_image(url: str, file_path: str, use_pil: bool = True, **kwargs) -> bool:
        """
        下载图片到本地
        :param url: 图片的url
        :param file_path: 图片的本地路径
        :param use_pil: 是否使用pil库进行图片处理
        :return: 是否下载成功
        """
        ImageHelper.get_image_from_url(url, use_pil=use_pil, **kwargs).save(file_path)
        return True
