# What is ddmail_validators
Python package for validating input for the DDMail project.

## What is DDMail
DDMail is a e-mail system/service that prioritizes security. A current production example can be found at www.ddmail.se

## Operating system
Developt for and tested on debian 12.

## Installing using pip
`pip install ddmail-validators`

## Building and installing from source using hatchling.
Step 1: clone github repo<br>
`git clone https://github.com/drzobin/ddmail_validators [code path]`<br>
`cd [code path]`<br>
<br>
Step 2: Setup python virtual environments<br>
`python -m venv [venv path]`<br>
`source [venv path]/bin/activate`<br>
<br>
Step 3: Install required dependencies<br>
`pip install -r requirements.txt`<br>
<br>
Step 4: Build package<br>
`python -m pip install --upgrade build`<br>
`python -m build `<br><br>
Packages is now located under dist folder<br>
<br>
Step 5: Install package<br>
`pip install dist/[package name].whl`

## Testing
`cd [code path]`<br>
`pytest --cov=ddmail_validators tests/`

## Coding
Follow PEP8 and PEP257. Use Ruff or Flake8 with flake8-docstrings for linting. Strive for 100% test coverage.
