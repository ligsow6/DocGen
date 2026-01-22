"""Logging setup for DocGen."""

import logging as pylogging


def setup_logging(verbose: bool = False) -> pylogging.Logger:
    level = pylogging.DEBUG if verbose else pylogging.INFO
    pylogging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    return pylogging.getLogger("docgen")


def get_logger() -> pylogging.Logger:
    return pylogging.getLogger("docgen")
