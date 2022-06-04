from setuptools import find_packages, setup
from uc_semantic_layer import __version__

setup(
    name="uc_semantic_layer",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    install_requires=["pyyaml"],
    version=__version__,
    description="",
    author="",
)
