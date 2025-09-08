"""
Setup script for PyBookLid
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pybooklid",
    version="1.0.0",
    author="tcsenpai",
    author_email="tcsenpai@discus.sh",
    description="MacBook lid angle sensor library for Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tcsenpai/pybooklid",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "audio": ["numpy>=1.20.0", "sounddevice>=0.4.0", "scipy>=1.7.0"],
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "pybooklid-demo=pybooklid.examples.simple_usage:main",
            "pybooklid-monitor=pybooklid.examples.monitor_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pybooklid": ["examples/*.py"],
    },
    keywords="macbook lid angle sensor hid macos hardware",
    project_urls={
        "Bug Reports": "https://github.com/tcsenpai/pybooklid/issues",
        "Source": "https://github.com/tcsenpai/pybooklid",
        "Documentation": "https://github.com/tcsenpai/pybooklid/blob/main/README.md",
    },
)