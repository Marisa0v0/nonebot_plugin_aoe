import setuptools


with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setuptools.setup(
    name="nonebot_plugin_aoe",
    description="适用于 Nonebot2 的帝国时代 2 小游戏插件。",
    version="0.1.0",
    author="Marisa0v0",
    author_email="3290453320@qq.com",
    keywords=["nonebot2", "pip", "nonebot", "nonebot_plugin"],
    url="https://github.com/Marisa0v0/nonebot_plugin_aoe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    platforms="any",
    python_requires=">=3.8",
    install_requires=[
        'nonebot-adapter-onebot>=2.2.0',
        'nonebot2>=2.0.0rc2',
        'pillow~=10.3.0',
        'dacite=1.8.1'
    ]
)
