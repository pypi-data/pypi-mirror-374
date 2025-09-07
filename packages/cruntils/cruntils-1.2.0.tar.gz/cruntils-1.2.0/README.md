# Introduction

A collection of utilities. Mainly for me. Others may find them useful.

# Distribution

This package is available for download from the Python Package Index (PyPI).

https://pypi.org/project/cruntils/

`pip install cruntils`

# Updating package

To update the package, take the following steps:
- Delete the **/dist** folder (if it exists)
- Delete the **/cruntils.egg-info** folder (if it exists)
- Update the project version in **pyproject.toml**
- Build new package with **py -m build**
- Upload to PyPI with **py -m twine upload dist/\***

# Package Creation

Used the following guide to create the package:\
https://python-packaging.readthedocs.io/en/latest/minimal.html

This guide was also really useful:\
https://packaging.python.org/en/latest/tutorials/packaging-projects/