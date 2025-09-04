from setuptools import setup, find_packages
import os

setup(
    name="nushell_testing",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        'nushell_testing': ['data/*.exe'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nushell-test=nushell_testing.cli:main',
        ],
    },
    install_requires=[],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package that testing NuShell",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nushell_testing",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)