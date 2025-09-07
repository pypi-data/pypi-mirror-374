from setuptools import setup, find_packages

setup(
    name="biasvariance_toolkit",
    version="0.1.0",
    description="Bias–Variance decomposition toolkit for regression (MSE) and classification (0–1 loss)",
    author="Antony Ajay Geoffrey",
    author_email="ajaygeoffrey456@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "scikit-learn",
        "scipy"
    ],
    python_requires=">=3.8",
)
