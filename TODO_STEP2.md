# TODO Step 2 - Setup projet + architecture

- [ ] Initialize `pyproject.toml` with Python 3.11 target and basic metadata
- [ ] Create `src/docgen/` package with empty modules (cli, config, models, scan, build, render, io, errors)
- [ ] Define CLI entrypoint `docgen` wired to Typer or Click
- [ ] Implement config loader for `docgen.yaml` with defaults and validation
- [ ] Implement ProjectInfo dataclass in `models.py`
- [ ] Stub scan pipeline: file discovery with excludes and stack detection placeholders
- [ ] Stub build pipeline: marker parsing and replace strategy (no rendering yet)
- [ ] Add Markdown templates directory and initial skeleton templates
- [ ] Add basic logging setup and consistent exit codes
- [ ] Add unit test scaffold for config and marker parser
- [ ] Document developer workflow in a short `CONTRIBUTING.md`
