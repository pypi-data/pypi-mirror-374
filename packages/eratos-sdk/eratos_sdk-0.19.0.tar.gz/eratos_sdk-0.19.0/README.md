# Python SDK to interact with the Eratos Platform.
Copyright (c) Eratos Group Pty Ltd 2019-2025.

## Installation

Run the following to bring in the package dependencies and the SDK package.

```shell
pip install .
```

If you wish to develop locally, please install with the following command instead.

> Note: Use the `[-e/--editable]` flag to symlink local changes to the installed package.

```shell
pip install .[dev]
```

If you are using zsh...

```shell
pip install '.[dev]'
```

If you wish to make wheel or sdist build you can do so with the following with the hatchling backend:
```shell
hatch build
```

## Tests

To run tests make sure you have the `dev` dependencies installed and run the following:

```shell
pytest tests/
```

`pytest` will run both the legacy `python.unittest` tests as well as the new `pytest` tests but not the other way so using `pytest` is preferred onwards from now.
The choice to adopt `pytest` has been made to make use of test fixtures to speed up development of future tests.
See [latest pytest api reference](https://docs.pytest.org/en/latest/reference/reference.html) for more info or the [getting started docs](https://docs.pytest.org/en/latest/getting-started.html).

### Integration tests

Integration tests in `tests/test_add_objects.py` will be skipped if the environment variables `ERATOS_ID` and `ERATOS_SECRET` are unset.
Add these API key values in a `.env` file in the root of the project or export as an environment variable to run the tests.

