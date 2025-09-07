from setuptools import setup, find_packages
import re

with open("README.MD", "r", encoding="utf-8") as f:
    long_desc = f.read()

with open("kmbbank/__init__.py", "r", encoding="utf-8") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name="kmbbank",
    version=version,
    license="MIT",
    description="Unofficial Python API for MB Bank (repackaged as kmbbank)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/thedtvn/MBBank",
    author="Lê Khang",
    author_email="kmb247.com@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "aiohttp",
        "Pillow",
        "wasmtime",
        "mb-capcha-ocr>=0.1.5"
    ],

    include_package_data=True,
    python_requires=">=3.8",
)
