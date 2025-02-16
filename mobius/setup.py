from setuptools import setup, find_packages

setup(
    name="mobius",
    version="0.1",
    packages=find_packages(where="src"),  # <== Important
    package_dir={"": "src"},  # <== Important
)
