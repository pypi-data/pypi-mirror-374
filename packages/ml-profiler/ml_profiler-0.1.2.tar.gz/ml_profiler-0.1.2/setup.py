from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ml_profiler",
    version="0.1.2",  # bump again
    author="Divyanshu Chouhan",
    description="Automated ML profiling and reporting tool",
    long_description=long_description,
    long_description_content_type="text/markdown",  # this is crucial
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "shap"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)