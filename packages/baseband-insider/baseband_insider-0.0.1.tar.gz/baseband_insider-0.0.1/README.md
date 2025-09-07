# baseband_insider

Lightweight helpers to build the temporary protocol event stream in Python.

## Setup (Pipenv)

1. Install pipenv
2. From this directory:

```
pipenv install --dev
```

## Run tests

```
pipenv run test
```

## Run example

Examples live under `examples/`.

```
pipenv run example-openai
```

## Dev scripts

All commands run via Pipenv:

```
pipenv run lint           # Ruff checks
pipenv run fmt            # Ruff auto-fix
pipenv run test           # Pytest
pipenv run clean          # Remove build artifacts
pipenv run build          # Build sdist + wheel
pipenv run check-dist     # Twine check
pipenv run publish-test   # Upload to TestPyPI
pipenv run publish        # Upload to PyPI
```

## Release (TestPyPI → PyPI)

1. Bump the version in `pyproject.toml` under `[project] version`.

2. Build and check:

```
pipenv run clean && pipenv run build && pipenv run check-dist
```

3. Upload to TestPyPI:

```
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-TESTPYPI-... pipenv run publish-test
```

4. Verify install from TestPyPI (optional):

```
python3 -m venv /tmp/insider-venv && source /tmp/insider-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple baseband-insider
python -c "import baseband_insider as b; print(getattr(b, '__version__', 'ok'))"
```

5. Upload to PyPI:

```
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... pipenv run publish
```

## API

- `event_stack()`: context manager that collects emitted events in stack.events.
- `Section`, `Capsule`, `Text`, `Url`: mirror the temporary protocol.
- Property sets and `Text.append()` emit partial-update events as specified in `packages/database/types/temporary-protocol.md`.
