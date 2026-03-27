from setuptools import setup, find_packages
from pathlib import Path


NAME = "mconduit"
DESCRIPTION = "A tool to control multiple Minecraft servers with Python!"
PROJECT_URLS = {"Homepage": "https://github.com/1attila/Conduit"}
AUTHOR = "Attila"
REQUIRES_PYTHON = ">=3.11"

CLASSIFIERS = [
    "Development Status :: 4 - Beta",

    "Operating System :: OS Independent",

    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",

    "Typing :: Typed"
]

ENTRY_POINTS = {"console_scripts": ["mconduit = mconduit.__main__:main"]}

here = Path("C:\\Users\\Hp\\Desktop\\handler\\Conduit")

version = {}
with open(here.joinpath(here, "mconduit", "__version__.py")) as f:
    exec(f.read(), version)
VERSION = version["__version__"]

with open(here.joinpath(here, "requirements.txt")) as f:
	REQUIRED = list(filter(None, map(str.strip, f)))

with open(here.joinpath(here, "PYPI_README.md")) as f:
	LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="GPL-3.0-only",
	author=AUTHOR,
	python_requires=REQUIRES_PYTHON,
	project_urls=PROJECT_URLS,
	packages=find_packages(exclude=["assets*", "tests*", "examples*"]),
	include_package_data=True,
	install_requires=REQUIRED,
	classifiers=CLASSIFIERS,
	entry_points=ENTRY_POINTS,
)