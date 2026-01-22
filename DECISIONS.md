# Decisions

- Python 3.11 is the target runtime; 3.10 remains acceptable if a dependency requires it. Reason: typing features and modern stdlib.
- CLI framework: Typer (fallback Click if needed). Reason: typed parameters and clear help output.
- Dependency management: `pyproject.toml` with setuptools + pip (editable installs). Reason: minimal tooling, standard PEP 621 metadata.
- Config file: `docgen.yaml` in repo root with `output_dir` and `exclude`. Reason: minimal, explicit.
- Managed zones: HTML comment markers `<!-- DOCGEN:BEGIN id="..." -->` and matching END. Reason: robust, diff-friendly, language-agnostic.
- Output location: `output_dir` is the base for README and ARCHITECTURE; default `docs/`. Reason: avoid overwriting root by default.
- Rendering: Jinja2 templates (optional) or simple string templates. Reason: keep templates readable and extensible.
- Logging: stdlib `logging` to stderr, INFO by default, `--verbose` for DEBUG. Reason: no heavy deps.
- Errors: dedicated exit codes for config/scan/build; never modify files on marker corruption. Reason: safe idempotence.
- Module layout: `docgen/{cli.py,config.py,models.py,errors.py,logging.py,services/,utils/}`. Reason: separation of concerns without extra build tooling.
