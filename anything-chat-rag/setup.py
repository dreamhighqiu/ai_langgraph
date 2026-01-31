# Minimal setup.py for backward compatibility
# Primary configuration is now in pyproject.toml

from setuptools import setup, find_packages

setup(
    packages=find_packages(
        where=".",
        include=["lightrag*", "raganything*"],
        exclude=["tests*", "docs*", "examples*"],
    ),
)
