#!/usr/bin/env python
# -*- coding:utf-8 -*-
import io
import re
from setuptools import setup, find_packages

with io.open("README.md", 'r', encoding='utf-8') as f:
    long_description = re.sub(r':\w+:\s', '', f.read())  # Remove emoji

setup(
    name="ml-simple-notify",
    version="0.0.4",
    keywords=("notice", "notification", "微信通知", "钉钉通知", "bark通知", "消息通知"),
    description="一个简单可扩展的消息通知库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",

    url="https://github.com/mic1on/simple-notify",
    author="miclon",
    author_email="jcnd@163.com",

    packages=['notify',
              'notify/channels'],
    include_package_data=True,
    platforms="any"
)
