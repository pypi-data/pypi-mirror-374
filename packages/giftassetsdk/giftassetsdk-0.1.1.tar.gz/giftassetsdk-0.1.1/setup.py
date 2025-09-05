from setuptools import setup, find_packages
import codecs
import os

# Чтение README
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="giftassetsdk",
    version="0.1.1",
    author="KILLDABORNE",
    author_email="dev.nevermore696@email.com",
    description="sdk for @giftassetapi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-library",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp==3.10.11"
    ],
    keywords="python, library, giftassetapi, gift, asset, giftasset"
)