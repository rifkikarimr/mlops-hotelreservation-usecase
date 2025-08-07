from setuptools import setup,find_packages # type: ignore

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Hotel-Reservation-Project",
    version="0.1",      
    author="Karim",
    packages=find_packages(),
    install_requires = requirements
)