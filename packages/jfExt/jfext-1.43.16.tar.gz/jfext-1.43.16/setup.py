#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def update_current_version():
    # try:
    #     fp = open('version', 'r')
    #     [major, sub, rev] = fp.read().split('.')
    #     version = '{}.{}.{}'.format(major, sub, str(int(rev) + 1))
    #     fp.close()
    #     fp = open('version', 'w')
    #     fp.write(version)
    #     return version
    # except Exception:
    #     return "1.0.0"
    return "1.43.16"


setup(
    name="jfExt",
    version=update_current_version(),
    description="private common python framework",
    long_description="...",
    keywords="jfExt",
    author="jifu",
    author_email="ji.fu@icloud.com",
    url="http://www.jifu.nz",
    license="MIT",
    packages=find_packages(exclude=["test", "*.pyc"]),
    install_requires=[
        "flask",
        "flask_mail",
        "flask_redis",
        "six",
        "prettytable",
        "requests",
        "uuid",
        "validators",
        "geoip2",
        "icecream",
        "urllib3",
        "xlwt",
        "check-digit-EAN13",
        "numpy",
        "requests",
        "xlsxwriter",
        "pillow",
        "fake_useragent"
    ],
    extras_require={},
    package_data={
        # 指定 data 文件夹下所有 otf 文件都打包
        "jfExt": ["data/*.otf"]
    },
    include_package_data=True,
    zip_safe=True,
)
