from setuptools import setup, find_packages

setup(
    name="yhd-depchecker",  # 包名称：yhd-depchecker
    version="1.0.0",  # 第一个版本
    description="用于检测当前代码环境是否拥有开发者所要求的库，并安装。可用于直接分发代码快捷安装",  # 中文描述
    long_description=open("README.md", encoding="utf-8").read(),  # 从README.md读取详细描述
    long_description_content_type="text/markdown",  # 描述格式为markdown
    author="YHD gamepaly（颜华蝶游戏社）",  # 作者/组织名
    author_email="f17376088816@163.com",  # 作者邮箱
    url="",  # 项目地址暂空
    packages=find_packages(),  # 自动发现并包含所有包
    classifiers=[  # 分类器列表，帮助用户搜索和筛选包
        "Development Status :: 4 - Beta",  # 开发状态：测试版
        "Intended Audience :: Developers",  # 目标受众：开发者
        "License :: OSI Approved :: MIT License",  # 许可证：MIT
        "Programming Language :: Python :: 3",  # 支持Python 3
        "Programming Language :: Python :: 3.8",  # 支持Python 3.8
        "Programming Language :: Python :: 3.9",  # 支持Python 3.9
        "Programming Language :: Python :: 3.10",  # 支持Python 3.10
        "Programming Language :: Python :: 3.11",  # 支持Python 3.11
        "Programming Language :: Python :: 3.12",  # 支持Python 3.12
        "Topic :: Software Development :: Libraries",  # 主题：软件开发 -> 库
        "Topic :: System :: Installation/Setup",  # 主题：系统 -> 安装/设置
        "Topic :: Utilities",  # 主题：实用工具
    ],
    python_requires=">=3.8",  # Python版本要求：至少3.8版本
    keywords="dependency, checker, installer, package management, environment",  # 关键词
    install_requires=[],  # 项目依赖项（根据您提供的代码，暂无额外依赖）
)
