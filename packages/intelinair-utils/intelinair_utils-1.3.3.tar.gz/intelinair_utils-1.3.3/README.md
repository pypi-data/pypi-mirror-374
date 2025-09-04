# intelinair-utils

Set of common code to be used across a number of intelinair repos

Unit Test Coverage: ![](./assets/unit-coverage.svg)

Integration Test Coverage ![](./assets/integration-coverage.svg)

## Repository Structure

### scripts

Location for bash utility scripts

###  src

Location for package source code

### tests

Location for unit and integration tests for package

## Usage

### Development

Create a virtual environment and install the dev requirements

```bash
conda create -n intelinair-utils python=3.8
conda activate intelinair-utils
pip install -r requirements_dev.txt
```

### Code style
- max line length - 120
- docstring style - google

### Testing

To run the unit and integration tests: (requires a valid ~/.agmri.cfg)

```bash
./scripts/test.sh
```

View coverage html report at ./html/{unit|integration}_coverage/index.html

### Generate Documentation

All the docstrings can be rendered into html for easy viewing

```bash
./scripts/generate_docs.sh
```

View docs at ./html/docs/intelinair_utils/index.html

### Releasing

To release a new version run the following in the master branch being sure to specify the type of release.

```bash
./scripts/do_release.sh {patch|minor|major}
```

### Installing

To install this package run one of the following

```bash
# Install a specific version
pip install git+https://github.com/intelinair/intelinair-utils@v0.0.1

# Install the latest version
pip install git+https://github.com/intelinair/intelinair-utils
```

# Package Usage

## Requirements

1. Set up aws credentials. If you don't have credentials ask David Wilson
    ```bash
    pip install awscli
    aws configure
    ```
1. Set up agmri credentials (see [intelinair_utils.agmri_api](../src/intelinair_utils/agmri_api.py) for more details)
    ```bash
    echo '[prod]
    admin_username = <YOUR_USERNAME>
    admin_password = <YOUR_PASSWORD>
    ' > ~/.agmri.cfg
    ```

## Installation 

Install the latest version

```bash
pip install git+https://github.com/intelinair/intelinair-utils
```

## Usage

Start a python shell

```python
from intelinair_utils import AgmriApi

api = AgmriApi('prod')

print(api.get('flights/' + 'M933ZLYGP'))
```
