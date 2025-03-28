from setuptools import setup, find_packages
import os


NAME = "conduit"
DESCRIPTION = "A tool to control multiple Minecraft servers with Python!"
PROJECT_URLS = {"Homepage": "https://github.com/1attila/Conduit"}
AUTHOR = "Attila"
REQUIRES_PYTHON = ">=3.10"

CLASSIFIERS = [
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Development Status :: 4 - Beta",

    "Operating System :: OS Independent",

    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",

    "Typing :: Typed"
]

ENTRY_POINTS = {"console_scripts": ["conduit = conduit.__main__:main"]}

here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(here, "conduit", "__version__.py")) as f:
    exec(f.read(), version)
VERSION = version["__version__"]

with open(os.path.join(here, "requirements.txt")) as f:
	REQUIRED = list(filter(None, map(str.strip, f)))

with open(os.path.join(here, "README.md")) as f:
	LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version="0.1.0",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
	author=AUTHOR,
	python_requires=REQUIRES_PYTHON,
	project_urls=PROJECT_URLS,
	packages=find_packages(exclude=["tests*", "examples*"]),
	include_package_data=True,
	install_requires=REQUIRED,
	classifiers=CLASSIFIERS,
	entry_points=ENTRY_POINTS,
)