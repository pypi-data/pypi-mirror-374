from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pdecrypto",
    version="0.1.0",
    description="Position-Dependent Encryption (PDE) library with authentication and padding",
    author="QKing",
    author_email="qking@host4you.cloud",
    url="https://github.com/QKing-Official/pdecrypto",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography"
    ],
    install_requires=[
        "pytest>=7.0.0",
    ],
    include_package_data=True,
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
