from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='sscreen',
    version='0.2',
    packages=find_packages(),
    install_requires=['PyQt6'],
    description='A modern PyQt6 GUI library',  # short desc
    long_description=long_description,
    long_description_content_type='text/markdown',  # important
    author='Sanki',
    url='',  # GitHub link optional, blank is fine
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
