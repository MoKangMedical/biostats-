from setuptools import setup, find_packages

setup(
    name="biostats",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["biostats=biostats.__main__:main"]},
    description="AI-Powered Biostatistics Platform",
    author="MoKangMedical",
)
