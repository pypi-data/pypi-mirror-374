from setuptools import setup, find_packages

setup(
    name="fairness-garvit",  # PyPI package name
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "scikit-learn",
        "matplotlib"
    ],
    author="Garvit Gupta",
    description="A fairness-aware machine learning package implementing fairness-constrained models.",
    long_description="A fairness-aware ML algorithm package",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
