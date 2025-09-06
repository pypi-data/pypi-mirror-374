from setuptools import setup, find_packages

setup(
    name="fairml-garvit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "scikit-learn"
    ],
    author="Your Name",
    description="A fairness-aware ML algorithm package",
    url="https://github.com/yourusername/fairml",
    python_requires=">=3.7",
)
