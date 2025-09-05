from setuptools import setup, find_packages

setup(
    name="layclt",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "layclt=layclt.__main__:main",
        ],
    },
    python_requires=">=3.7",
)
