# Energy Services Simulation Backend (development branch)
---
The `backend` python module contains the necessary Object Oriented Python code needed for simulating Photo-Voltaic systems via different simulation software offerings.

The backend is designed to interface with:

1. NREL's python based SDK, [PySAM](https://sam.nrel.gov/software-development-kit-sdk/pysam.html), for the System Advisory Module ([SAM](https://sam.nrel.gov/)) [Photovoltaic](https://sam.nrel.gov/photovoltaic.html) module with the intent to compare against [Aurora Solar](https://aurorasolar.com/).

## Installation Instructions (tested on Ubuntu 22.04)
---
The `backend` module is managed by the `poetry` dependency management and packaging tool.

On a `Linux` machine, `poetry` is best installed within a virtual environment.

With Python 3, a virtual environment can be created as:

    user@computer:~$ python -m venev <path>/<env-name>
    
The virtual environment can be activated as follows:

    user@computer:~$ source <path>/<env_name>/bin/activate
    
To deactivate simply execute

    user@computer:~$`deactivate

Once in an active virtual environment, install `poetry` as follows:

    user@computer:~$ <path>/<env-name>/bin/pip install -U pip setuptools # update pip and setuptools
    user@computer:~$ <path>/<env-name>/bin/pip install poetry
    
To install the `backend`:

    user@computer:~$ cd backend
    user@computer:~$ poetry install
    
The `backend` comes shipped with unit-tests which can be by invoking:

    user@computer:~$ poetry run pytest

