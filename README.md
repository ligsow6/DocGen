# DocGen

DocGen is a CLI that will generate standardized Markdown documentation from a local Git repository.
This repository currently contains the project skeleton and stub commands (init/scan/build).

## Development setup

- Requires Python 3.11+
- Dependency management: `pyproject.toml` with setuptools + pip

Install in editable mode:

```
python -m pip install -e ".[dev]"
```

Run the CLI:

```
docgen --help
python -m docgen --help
```

Initialize configuration:

```
docgen init
```

Run stub scan/build:

```
docgen scan --format json

docgen build --dry-run
```

## Notes

- The current `scan` and `build` commands are stubs. They return deterministic demo data and do not scan the filesystem yet.
- See `docs/spec.md` for the detailed specification.
