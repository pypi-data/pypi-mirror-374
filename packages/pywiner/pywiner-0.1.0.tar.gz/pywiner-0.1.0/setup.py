from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pywiner",
    version="0.1.0",
    author="GuestRoblox Studios",
    author_email="maria.gomes23.1949@gmail.com",
    description="A Python library for Windows automation and a native window framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoVerify/pywiner",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
    install_requires=[
        "ctypes",
        "os"
        "subprocess"
        "tempfile"
    ],
)