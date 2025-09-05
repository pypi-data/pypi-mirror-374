from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join("README", "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A fast, interactive Python project generator that eliminates repetitive setup tasks."

setup(
    name="newproj-bobv1",
    version="1.0.0",
    author="Liam G",
    author_email="TemNet021@outlook.com",
    description="A fast, interactive Python project generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Golden021/newproj",
    project_urls={
        "Bug Reports": "https://github.com/Golden021/newproj/issues",
        "Source": "https://github.com/Golden021/newproj",
        "Documentation": "https://github.com/Golden021/newproj#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "newproj=newproj.cli:main",
        ],
    },
    install_requires=[],
    keywords="python project generator boilerplate template cli interactive pygame",
    include_package_data=True,
)