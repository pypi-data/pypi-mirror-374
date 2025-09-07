from setuptools import setup, find_packages

setup(
    name="pyscriptbase",  # 包名
    version="1.0.1",  # 版本号
    packages=find_packages(),  # 自动查找包
    author="ASMan",
    author_email="",
    description="python script base library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",  # 项目主页
    install_requires=[
        "loguru",
        "selenium",
        "pymysql",
        "pycryptodome",
        "pyyaml",
        "xmltodict",
        "prettytable",
        "pyjwt",
        "fake_useragent",
        "beautifulsoup4",
        "requests",
        "lxml",
    ],  # 依赖包列表
)
