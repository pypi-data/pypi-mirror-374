# dcat-ms-ap

A dcat ap implementing the recommendations fo the MS MIChI.

## Website

[https://NFDI4Chem.github.io/dcat-ms-ap](https://NFDI4Chem.github.io/dcat-ms-ap)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [dcat_ms_ap](src/dcat_ms_ap)
    * [schema](src/dcat_ms_ap/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/dcat_ms_ap/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install rust-just
uv pip install poetry

```



## Developer Documentation

<details>
To run commands you may use good old make or the command runner [just](https://github.com/casey/just/) which is a better choice on Windows.
Use the `make` command or `duty` commands to generate project artefacts:
* `make help` or `just --list`: list all pre-defined tasks
* `make all` or `just all`: make everything
* `make deploy` or `just deploy`: deploys site
</details>

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).
