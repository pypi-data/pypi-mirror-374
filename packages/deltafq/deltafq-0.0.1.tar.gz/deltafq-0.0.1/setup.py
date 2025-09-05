from setuptools import setup, find_packages

setup(
    name="deltafq",
    version="0.0.1",
    packages=find_packages(),
    description="A powerful quantitative trading framework for Python.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="DeltaF",
    author_email="leek_li@outlook.com",
    url="https://github.com/Delta-F/DeltaFQ",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)