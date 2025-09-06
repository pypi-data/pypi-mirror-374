from setuptools import setup, find_packages

setup(
    name="pylove2d",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "pygame-ce>=2.5.3",
        "numpy>=1.24"
    ],
    python_requires=">=3.10",
)
