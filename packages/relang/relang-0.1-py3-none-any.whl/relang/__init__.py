"""Relang.

Self hosted, simplest possible web interface for text translations using Meta's
NLLB200 model."""

__version__ = "0.1"


def cli():
    "Target for [project.scripts]."
    from . import __main__
