import os
from setuptools import setup, find_packages

setup(
    name="popat",
    version="0.1.3",
    description="Intelligent Terminal Error Helper - Advanced error detection and analysis for developers",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Anirudh Sajith",
    author_email="anirudhsajith03@gmail.com",
    url="https://github.com/An1rud/popat",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4", 
        "psutil>=5.8.0",
    ],
    entry_points={
        "console_scripts": [
            "popat=popat_python.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)