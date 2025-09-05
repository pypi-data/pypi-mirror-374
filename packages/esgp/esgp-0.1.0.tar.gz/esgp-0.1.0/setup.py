from setuptools import setup, find_packages
import codecs
import os

# Read the contents of your README file
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="esgp",
    version="0.1.0",
    author="Ronin Akagami",
    author_email="roninakagami@proton.me",
    description="Echo State Gradient Propogation implementation for PyTorch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoninAkagami/esgp-net",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "torch>=1.9.0",
    ],
    keywords="pytorch, reservoir computing, echo state network, esn, esgp",
    project_urls={
        "Bug Reports": "https://github.com/RoninAkagami/esgp-net/issues",
        "Source": "https://github.com/RoninAkagami/esgp-net",
    },
)