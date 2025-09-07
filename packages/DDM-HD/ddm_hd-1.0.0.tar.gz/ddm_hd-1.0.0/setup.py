"""
DDM-HD库的setup.py文件
用于打包和发布到PyPI
"""
# pylint: disable=import-error
from setuptools import setup, find_packages  # type: ignore


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="DDM-HD",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Digital Distribution Management - A library for license key verification and management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DDM-HD",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
)