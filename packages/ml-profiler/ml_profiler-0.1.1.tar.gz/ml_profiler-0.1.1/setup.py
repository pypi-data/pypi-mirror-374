from setuptools import setup, find_packages

setup(
    name="ml_profiler",
    version="0.1.1",
    author="Divyanshu Chouhan",
    description="Automated ML profiling and reporting tool",
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