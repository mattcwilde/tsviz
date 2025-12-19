from setuptools import setup, find_packages

setup(
    name="tsviz",
    version="1.0.0",
    description="Interactive time series visualization CLI tool",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "plotly>=5.0.0",
        "pandas>=1.3.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tsviz=tsviz.cli:main",
        ],
    },
    python_requires=">=3.7",
)
