import os
import re
from setuptools import setup, find_packages

def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()
    
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8-sig") as f:
        required_packages = f.read().splitlines()
else:
    required_packages = []

def get_version():
    return "0.1.0"

setup(
    name="SpotDown",
    version=get_version(),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Arrowar",
    url="https://github.com/Arrowar/SpotDown",
    packages=find_packages(include=["SpotDown", "SpotDown.*"]),
    install_requires=required_packages,
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "spotdown=SpotDown.main:run",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/Arrowar/SpotDown/issues",
        "Source": "https://github.com/Arrowar/SpotDown"
    }
)
