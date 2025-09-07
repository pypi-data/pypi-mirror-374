# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloViro",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyperclip",
        "pyautogui",
        "python-dotenv"
        "uv"
    ],
    author="Tristan McBride Sr.",
    author_email="142635792+TristanMcBrideSr@users.noreply.github.com",
    description="Thread-safe, singleton virtual environment manager for rapid code generation, safe pip installs, and sandboxed Python automation.",
)
