"""Offline report rendering for recorded observation runs."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoadedObservations:
    observations: list[dict[str, Any]]
    warnings: list[str]


def load_observations(path: str | Path) -> LoadedObservations:
    """Load JSONL observations, tolerating a truncated final line."""

    observations: list[dict[str, Any]] = []
    warnings: list[str] = []
    with Path(path).open("r", encoding="utf-8") as stream:
        lines = stream.readlines()

    numbered = [
        (number + 1, line)
        for number, line in enumerate(lines)
        if line.strip()
    ]
    for position, (number, value) in enumerate(numbered):
        try:
            item = json.loads(value)
        except json.JSONDecodeError as error:
            if position == len(numbered) - 1:
                warnings.append(
                    f"ignored truncated final observation at line {number}"
                )
                break
            raise ValueError(
                f"invalid observation JSON at line {number}"
            ) from error
        if not isinstance(item, dict):
            raise ValueError(f"observation at line {number} must be an object")
        observations.append(item)
    return LoadedObservations(observations=observations, warnings=warnings)


def _provider_surface(
    provider_id: str, profiles: Mapping[str, Mapping[str, Any]]
) -> str:
    return str(profiles.get(provider_id, {}).get("surface_equivalence", "unknown"))


def summarize_observations(
    observations: Sequence[Mapping[str, Any]],
    profiles: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for observation in observations:
        key = (str(observation.get("probe_id")), str(observation.get("provider_id")))
        grouped[key].append(observation)

    rows: list[dict[str, Any]] = []
    for (probe_id, provider_id), values in sorted(grouped.items()):
        statuses = Counter(str(value.get("status")) for value in values)
        categories = Counter(
            str(value.get("evidence_category"))
            for value in values
            if value.get("evidence_category") is not None
        )
        urls: set[str] = set()
        for value in values:
            for citation in value.get("citations", []) or []:
                if isinstance(citation, dict) and citation.get("url"):
                    urls.add(str(citation["url"]))
                elif isinstance(citation, str):
                    urls.add(citation)
        latencies = [
            float(value["latency_ms"])
            for value in values
            if isinstance(value.get("latency_ms"), (int, float))
            and not isinstance(value.get("latency_ms"), bool)
        ]
        costs = [
            float(value["cost_usd"])
            for value in values
            if isinstance(value.get("cost_usd"), (int, float))
        ]
        tokens = sum(
            int(total)
            for value in values
            for total in (value.get("token_usage") or {}).values()
            if isinstance(total, int)
        )
        rows.append(
            {
                "probe_id": probe_id,
                "provider_id": provider_id,
                "consumer_surface": _provider_surface(provider_id, profiles),
                "samples": len(values),
                "ok": statuses.get("ok", 0),
                "error": statuses.get("error", 0),
                "status_refused": statuses.get("refused", 0),
                "brand_with_citation": categories.get("brand_with_citation", 0),
                "brand_mentioned": categories.get("brand_mentioned", 0),
                "citation_only": categories.get("citation_only", 0),
                "not_cited": categories.get("not_cited", 0),
                "refused_or_unsearchable": categories.get(
                    "refused_or_unsearchable", 0
                ),
                "unique_cited_urls": len(urls),
                "total_cost_usd": sum(costs) or None,
                "total_tokens": tokens,
                "mean_latency_ms": (
                    round(sum(latencies) / len(latencies)) if latencies else None
                ),
            }
        )
    return rows


CSV_COLUMNS = (
    "probe_id",
    "provider_id",
    "consumer_surface",
    "samples",
    "ok",
    "error",
    "status_refused",
    "brand_with_citation",
    "brand_mentioned",
    "citation_only",
    "not_cited",
    "refused_or_unsearchable",
    "unique_cited_urls",
    "total_cost_usd",
    "total_tokens",
    "mean_latency_ms",
)


def render_csv(rows: Sequence[Mapping[str, Any]], path: str | Path) -> Path:
    output_path = Path(path)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _report_group(consumer_surface: str) -> str:
    if consumer_surface in {"direct", "partial", "proxy"}:
        return "AI-search visibility"
    if consumer_surface == "no":
        return "Model capability baseline"
    return "Unclassified surface"


def render_html(
    *,
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    warnings: Sequence[str],
    path: str | Path,
) -> Path:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[_report_group(str(row["consumer_surface"]))].append(row)

    def table(items: Sequence[Mapping[str, Any]]) -> str:
        if not items:
            return "<p>No observations in this section.</p>"
        head = "".join(f"<th>{html.escape(column)}</th>" for column in CSV_COLUMNS)
        body_parts = []
        for item in items:
            cells = [
                f"<td>{html.escape(str(item.get(column)))}</td>"
                for column in CSV_COLUMNS
            ]
            body_parts.append(f"<tr>{''.join(cells)}</tr>")
        return (
            "<table><thead><tr>"
            f"{head}</tr></thead><tbody>{''.join(body_parts)}</tbody></table>"
        )

    warning_items = "".join(
        f"<li>{html.escape(warning)}</li>" for warning in warnings
    )
    warnings_html = f'<ul class="warning">{warning_items}</ul>' if warnings else ""
    sections = []
    for group in (
        "AI-search visibility",
        "Model capability baseline",
        "Unclassified surface",
    ):
        sections.append(
            f"<h2>{html.escape(group)}</h2>{table(groups.get(group, []))}"
        )

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>AI citation probe report</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
th, td {{ border: 1px solid #ccc; padding: .45rem; text-align: left; }}
th {{ background: #f3f4f6; }}
.warning {{ color: #92400e; }}
</style></head><body>
<h1>AI citation probe report</h1>
<p>Run: {html.escape(str(manifest.get('run_id')))} ·
Probe set: {html.escape(str(manifest.get('probe_set_version')))} ·
Hash: <code>{html.escape(str(manifest.get('probe_set_hash')))}</code></p>
<p>This report separates AI-search visibility from no-search model-capability
baselines. It reports observations and evidence counts, not a synthetic ranking.</p>
{warnings_html}
{''.join(sections)}
</body></html>
"""
    output_path = Path(path)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def write_report(
    *, run_dir: str | Path, manifest: Mapping[str, Any]
) -> tuple[Path, Path]:
    directory = Path(run_dir)
    observations_path = directory / "observations.jsonl"
    if not observations_path.is_file():
        raise FileNotFoundError(
            f"missing run file: {observations_path}"
        )
    loaded = load_observations(observations_path)
    profiles_path = directory / "profiles.json"
    profiles: dict[str, dict[str, Any]] = {}
    if profiles_path.exists():
        values = json.loads(profiles_path.read_text(encoding="utf-8"))
        profiles = {str(item.get("id")): item for item in values}
    rows = summarize_observations(loaded.observations, profiles)
    csv_path = render_csv(rows, directory / "summary.csv")
    html_path = render_html(
        manifest=manifest,
        rows=rows,
        warnings=loaded.warnings,
        path=directory / "report.html",
    )
    return csv_path, html_path
