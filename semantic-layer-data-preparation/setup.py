"""
This file configures the Python package with entrypoints used for future runs on Databricks.

Please follow the `entry_points` documentation for more details on how to configure the entrypoint:
* https://setuptools.pypa.io/en/latest/userguide/entry_point.html
"""

from setuptools import find_packages, setup
from semantic_layer_data_preparation import __version__

setup(
    name="semantic_layer_data_preparation",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    install_requires=[
        "pyyaml"
    ],
    entry_points = {
        "console_scripts": [
            "etl = semantic_layer_data_preparation.workloads.sample_etl_job:entrypoint",
            "ml = semantic_layer_data_preparation.workloads.sample_ml_job:entrypoint"
    ]},
    version=__version__,
    description="",
    author="",
)
