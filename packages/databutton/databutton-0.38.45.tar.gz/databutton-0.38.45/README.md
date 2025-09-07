# databutton-cli
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![PyPI version fury.io](https://badge.fury.io/py/databutton.svg)](https://pypi.python.org/pypi/databutton/)
[![PyPI download week](https://img.shields.io/pypi/dw/databutton.svg)](https://pypi.python.org/pypi/databutton/)
![release](https://github.com/databutton/databutton-cli/actions/workflows/release.yaml/badge.svg)


The CLI for building and deploying databutton projects

## Getting Started

```bash
Usage: databutton [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose  Enable verbose logging
  --help         Show this message and exit.

Commands:
  build    Build the project, built components will be found in .databutton
  create   Create a Databutton project in the provided project-directory
  deploy   Deploy your project to Databutton
  docs     Launches https://docs.databutton.com
  init     Creates a new project in Databutton and writes to databutton.json
  login    Login to Databutton
  logout   Removes all Databutton login info
  serve    Starts a web server for production.
  start    Run the Databutton development server
  version  Get the library version.
  whoami   Shows the logged in user
```

## Developing

### Prerequisites
This project uses poetry, so if you haven't already;

`pip install poetry`

### Install dependencies

`poetry install`

### Test

`poetry run pytest -s`

### Lint
`make lint``

All these are being run in a github action on pull requests and the main branch.

### Test locally in another package

To test in another package, you can simply

`pip install -e .` assuming you're in this folder. If not, replace the `.` with the path to the `databutton-cli` folder.

## Authors

* **Databutton** - *Initial work* - [github](https://github.com/databutton)

## License: Copyright (c) Databutton

All rights reserved.
