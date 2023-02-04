# -*- coding: utf-8 -*-
# @Time    :   2022/08/16 21:48:13
# @Author  :   ddvv
# @公众号   :   NextB
# @File    :   setup.py
# @Software:   Visual Studio Code
# @Desc    :   None


import setuptools


def read_version():
    """
    读取打包的版本信息
    """
    with open("./nextbv2/version.py", "r", encoding="utf8") as f:
        for data in f.readlines():
            if data.startswith("NEXTB_V2_VERSION"):
                data = data.replace(" ", "")
                version = data.split("=")[-1][1:-1]
                return version
    # 默认返回
    return "2.0.0"


def read_readme():
    """
    读取README信息
    """
    with open("./README.md", "r", encoding="utf8") as f:
        return f.read()


def do_setup(**kwargs):
    try:
        setuptools.setup(**kwargs)
    except (SystemExit, Exception) as e:
        exit(1)


version = read_version()
long_description = read_readme()

do_setup(
    name="nextbv2",
    version=version,
    author="ddvv",
    author_email="dadavivi512@gmail.com",
    description="币安量化交易实验程序",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a232319779/nexbv2",
    packages=setuptools.find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "nextb-v2-data-process = nextbv2.libs.cli.data_process:run",
            "nextb-v2-data-statics = nextbv2.libs.cli.data_statics:run",
            "nextb-v2-trade = nextbv2.libs.cli.cli_trade:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords=[],
    license="MIT",
    include_package_data=True,
    install_requires=["python-binance==1.0.15", "tqdm==4.62.3", "numpy"],
)
