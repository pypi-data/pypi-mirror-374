from setuptools import setup

setup(
    name="layclt",
    version="1.0.1",
    py_modules=["layclt"],
    entry_points={
        "console_scripts": [
            "layclt=layclt:main",
        ],
    },
    python_requires=">=3.7",
)
