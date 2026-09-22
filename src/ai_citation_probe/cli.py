"""Command-line entry point.

The implementation intentionally stays minimal until the probe-set schema and
repository name are finalized. Commands are exposed early so their contracts
can be reviewed before the M1 provider integration.
"""

from __future__ import annotations

import argparse

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-citation-probe",
        description="Run reproducible AI citation measurements.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main() -> int:
    build_parser().parse_args()
    return 0
