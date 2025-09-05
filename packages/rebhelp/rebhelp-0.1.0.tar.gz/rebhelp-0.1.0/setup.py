from setuptools import setup, find_packages

from setuptools import setup, find_packages

setup(
    name="rebhelp",
    version="0.1.0",
    author="Arvill Abbineni",
    author_email="arvillacl17@gmail.com",
    description="Helper package for REBOUND: units, simulation generators, and orbital hierarchy utilities",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # automatically finds rebhelp/
    python_requires=">=3.8",
    install_requires=[
        "rebound>=3.0.0",
        "numpy>=1.20"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
    ],
)