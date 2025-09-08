#!/usr/bin/env python3
from setuptools import setup

setup(
    name="bash-script-maker",
    version="1.2.1",
    py_modules=["bash_script_maker", "syntax_highlighter", "localization", "custom_dialogs", "assets"],
    entry_points={
        "console_scripts": [
            "bash-script-maker=bash_script_maker:main",
        ],
    },
    install_requires=[
        "ttkbootstrap>=1.10.1",
        "pygments>=2.15.1",
    ],
)