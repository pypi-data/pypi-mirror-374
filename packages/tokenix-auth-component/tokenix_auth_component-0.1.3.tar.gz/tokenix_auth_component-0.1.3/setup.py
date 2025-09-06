#!/usr/bin/env python3
"""
Setup script for auth_component package
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Dependencias mínimas
requirements = [
    "requests>=2.25.0",
    "python-dotenv>=0.19.0"
]

setup(
    name="tokenix-auth-component",
    version="0.1.3",
    author="Edwin Caicedo Venté",
    author_email="ecaicedo@rapicredit.com",
    description="Componente de autenticación reutilizable para lambdas de RapidCredit que requieran autenticarse en Tokenix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/rapicredit/tokenix-auth-component",  # Repo privado
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
