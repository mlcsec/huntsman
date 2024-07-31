from setuptools import setup, find_packages
import os

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

requirements = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [x.strip() for x in f.readlines()]

setup(
    name="huntsman",
    version="0.5.2",
    packages=find_packages(),
    author="mlcsec",
    author_email="mlcsec@proton.me",
    description="Email enumerator, validator, and username generator for the hunter.io, snov.io, and skrapp.io APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mlcsec/huntsman",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "huntsman=huntsman.__main__:main",
        ],
    }
)