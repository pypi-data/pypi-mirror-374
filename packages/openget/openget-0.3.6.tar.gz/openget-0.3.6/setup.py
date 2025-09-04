# coding:utf8
from setuptools import setup, find_packages

from openget import version

setup(
    name="openget",
    version=version,
    description="A Spider FrameWork",
    long_description=open("README.MD", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    author="Dytttf",
    author_email="dytttf@foxmail.com",
    url="https://github.com/dytttf/openget",
    packages=find_packages(),
    install_requires=[
        "gevent",
        "pymysql",
        # "mysqlclient",
        "redis>=3.0.0",
        "better-exceptions",
        "tqdm",
        "httpx[http2]",
        "user-agent2",
        "urllib3",
        "python-dotenv",
    ],
    license="BSD",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Scrapy",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],
    keywords=["openget", "spider", "batch-spider"],
)
