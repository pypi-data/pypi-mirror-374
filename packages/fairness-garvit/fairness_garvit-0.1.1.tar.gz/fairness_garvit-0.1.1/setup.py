from setuptools import setup, find_packages

setup(
    name="fairness-garvit",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "scikit-learn",
        "matplotlib"
    ],
    author="Garvit Gupta",
    description="A fairness-aware ML algorithm package",
    long_description="Fairness-aware ML algorithm for reducing bias in predictive models.",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
