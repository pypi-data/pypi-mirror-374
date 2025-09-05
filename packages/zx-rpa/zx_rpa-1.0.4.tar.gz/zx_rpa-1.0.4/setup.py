import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))



# you need to change all these
VERSION = '1.0.4'
DESCRIPTION = '对常见的功能函数和一些平台的API进行封装'

setup(
    name="zx_rpa",
    version=VERSION,
    author="zang xin",
    author_email="zangxincz@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests",
        "loguru"
    ],
    extras_require={
        "qiniuyun": ["qiniu"],
        "all": ["qiniu"]
    },
    python_requires=">=3.12",
)
