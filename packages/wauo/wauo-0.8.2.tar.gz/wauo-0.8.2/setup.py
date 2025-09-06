# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='wauo',
    version='0.8.1',
    description='爬虫者的贴心助手',
    url='https://github.com/markadc/wauo',
    author='WangTuo',
    author_email='markadc@126.com',
    packages=find_packages(),
    license='MIT',
    zip_safe=False,
    install_requires=['requests', 'parsel', 'fake_useragent', 'loguru'],
    keywords=['Python', 'Spider'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
