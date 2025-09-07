from setuptools import setup, find_packages
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='Converter_machine',
    version='1.0.2',
    description='A unit conversion library for time, mass, length, temperature, and more',
    long_description=long_description, 
    long_description_content_type='text/markdown',  
    author='Amir M. Kimiaei',
    author_email="a.m.kimiaei84@email.com",
    url="https://github.com/AmirKimiaei/converter_machine",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
         "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
    ],
)
