"""Command-line entry point for M1 measurement runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import unquote

from . import __version__
from .manifest import build_manifest
from .probe_set import load_probe_set
from .providers.perplexity import PerplexityProvider
from .report import write_report
from .runner import run_probe_set


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-citation-probe",
        description="Run reproducible AI citation measurements.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a probe set")
    validate.add_argument("--probe-set", required=True)

    run = subparsers.add_parser(
        "run", help="run one provider against a validated probe set"
    )
    run.add_argument("--probe-set", required=True)
    run.add_argument("--profiles", required=True)
    run.add_argument("--provider", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument(
        "--slot",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="probe template slot value; repeat as needed",
    )
    report = subparsers.add_parser(
        "report", help="render CSV/HTML from a recorded run"
    )
    report.add_argument("--run-dir", required=True)
    return parser


def _select_profile(profiles_path: str, provider_id: str) -> dict:
    profiles = json.loads(Path(profiles_path).read_text(encoding="utf-8"))
    matches = [
        item
        for item in profiles.get("providers", [])
        if item.get("id") == provider_id
    ]
    if len(matches) != 1:
        raise ValueError(f"provider {provider_id!r} must appear exactly once")
    if provider_id != "perplexity-sonar":
        raise ValueError(f"transport is not implemented yet for {provider_id!r}")
    return matches[0]


def _run(args: argparse.Namespace) -> int:
    probe_set = load_probe_set(args.probe_set)
    profile = _select_profile(args.profiles, args.provider)
    profiles = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
    provider = PerplexityProvider(model=profile["model"])
    slots = {
        unquote(key): unquote(value)
        for key, value in (item.split("=", 1) for item in args.slot)
    }
    manifest = build_manifest(
        run_id=args.run_id,
        probe_set=probe_set,
        providers=profiles.get("providers", []),
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "profiles.json").write_text(
        json.dumps(profiles.get("providers", []), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    observations_path = run_probe_set(
        probe_set=probe_set,
        provider=provider,
        slots=slots,
        output_dir=output_dir,
    )
    print(observations_path)
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        load_probe_set(args.probe_set)
        print("ok")
        return 0
    if args.command == "run":
        return _run(args)
    if args.command == "report":
        manifest = json.loads(
            (Path(args.run_dir) / "manifest.json").read_text(encoding="utf-8")
        )
        csv_path, html_path = write_report(
            run_dir=args.run_dir, manifest=manifest
        )
        print(csv_path)
        print(html_path)
        return 0
    return 1
