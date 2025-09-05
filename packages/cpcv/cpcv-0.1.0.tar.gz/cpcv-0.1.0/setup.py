from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

# read README for long description
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cpcv",  # PyPI package name
    version="0.1.0",
    author="Yosri Ben Halima",
    author_email="yosri.benhalima@ept.ucar.tn",
    description="CPCV with Embargo for financial train-test splitting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yosri-Ben-Halima/cpcv",
    packages=find_packages(include=["cpcv", "cpcv.*"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21",
        "pandas>=1.5",
        "scikit-learn>=1.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Office/Business :: Financial :: Investment"
    ],
)
