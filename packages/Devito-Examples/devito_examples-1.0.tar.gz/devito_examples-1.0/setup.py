from pathlib import Path
from setuptools import setup, find_packages

README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name='Devito-Examples',
    version='1.0',
    description="Seismic modeling and inversion examples using Devito.",
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/slimgroup/Devito-Examples',
    author="Georgia Institute of Technology, SLIM Group",
    author_email='mlouboutin3@gatech.edu',
    license='MIT',
    packages=find_packages(include=["seismic", "seismic.*"]),
    include_package_data=True,
    install_requires=['devito[extras,tests]'],
    python_requires=">=3.8",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    project_urls={
        'Documentation': 'https://slimgroup.github.io/Devito-Examples/',
        'Source': 'https://github.com/slimgroup/Devito-Examples',
    },
)
