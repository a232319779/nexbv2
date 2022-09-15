# -*- coding: utf-8 -*-
# @Time    :   2022/08/16 21:48:13
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   setup.py
# @Software:   Visual Studio Code
# @Desc    :   None


from setuptools import setup, find_packages

depends = []

setup(
    name="nextbv2",
    version="2.0.0",
    packages=find_packages(exclude=[]),

    zip_safe=False,

    entry_points={
        "console_scripts": [
            "nextbv2-data-process = nextbv2.libs.cli.data_process:run",
        ],
    },

    install_requires=depends,

    dependency_links=[
    ],

    include_package_data=True,

    license="ddvv",

    author="ddvv",
    author_email="dadavivi512@gmail.com",
    description="nextb2.0",
)