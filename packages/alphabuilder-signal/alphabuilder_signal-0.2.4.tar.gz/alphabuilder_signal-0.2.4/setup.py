from setuptools import setup, find_packages


with open("README.MD", "r") as f:
    description = f.read()

setup(
    name="alphabuilder_signal",
    version='0.2.4',
    packages=find_packages(),
    install_requires = [
        # dependencies
    ],
    entry_points={
        "console_scripts": [
            "alphabuilder_signal = indicators:TechnicalIndicators"
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
    description="Alpha signal library for quantitative finance research"
)