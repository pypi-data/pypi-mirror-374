# coding: utf-8
import setuptools

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="QEventManager",
    version="1.0.1",
    keywords="Qt事件处理",
    author="赤鸢仙人",
    author_email="2640610281@qq.com",
    description="QEventManager使用多线程的方式对任务进行处理，qasync的另一个替代",
    long_description=long_description,
    long_description_content_type='text/markdown',
    # license="AGPL-3.0",
    url="https://gitee.com/chiyaun/qevent-manager",
    packages=setuptools.find_packages(),
    platforms=["all"],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "pillow"
    ],
    extras_require={},
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
    project_urls={
        'Project Homepage': 'https://gitee.com/chiyaun/qevent-manager',
        'Documentation': 'https://gitee.com/chiyaun/qevent-manager/blob/master/README.md',
        'Source Code': 'https://gitee.com/chiyaun/qevent-manager',
        'Bug Tracker': 'https://gitee.com/chiyaun/qevent-manager/issues',
    }
)
# pip freeze > requirements.txt
# 打包命令
# python setup.py sdist build
# 上传命令
# twine upload dist/qeventmanager-1.0.0.tar.gz
