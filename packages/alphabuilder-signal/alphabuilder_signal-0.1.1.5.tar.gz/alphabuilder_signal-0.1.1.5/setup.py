from setuptools import setup, find_packages


with open("README.MD", "r") as f:
    description = f.read()


setup(
    name="alphabuilder_signal",
    version="0.1.1.5",
    description="Alpha signal library for quantitative finance research",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Geet Mukherjee",
    author_email="mukherjeegeet3@gmail.com",
    url="https://pypi.org/project/alphabuilder-signal/",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yfinance>=0.2,<0.3",
        "pandas>=1.3,<3.0",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
)
