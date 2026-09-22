"""Execute a probe set and retain raw evidence plus normalized observations."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import ProviderObservation
from .probe_set import ProbeSet, render_probe
from .providers.base import CitationProvider


class RunRecorder:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.raw_dir = self.output_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.observations_path = self.output_dir / "observations.jsonl"
        self._observations: list[ProviderObservation] = []

    def add(self, observation: ProviderObservation, raw_response: Any) -> None:
        relative_raw = (
            f"raw/{observation.probe_id}-{observation.provider_id}-"
            f"{observation.sample_index}.json"
        )
        raw_path = self.output_dir / relative_raw
        raw_path.write_text(
            json.dumps(
                raw_response, ensure_ascii=False, sort_keys=True, indent=2
            ),
            encoding="utf-8",
        )
        values = asdict(observation)
        values["raw_response_uri"] = relative_raw
        self._observations.append(ProviderObservation(**values))

    def flush(self) -> Path:
        with self.observations_path.open("w", encoding="utf-8") as stream:
            for observation in self._observations:
                stream.write(
                    json.dumps(
                        asdict(observation), ensure_ascii=False, sort_keys=True
                    )
                    + "\n"
                )
        return self.observations_path


def run_probe_set(
    *,
    probe_set: ProbeSet,
    provider: CitationProvider,
    slots: dict[str, str],
    output_dir: str | Path,
) -> Path:
    recorder = RunRecorder(output_dir)
    samples = int(probe_set.defaults["samples_per_run"])
    temperature = float(probe_set.defaults["temperature"])
    for probe in probe_set.probes:
        rendered = render_probe(probe, slots)
        for sample_index in range(samples):
            observation, raw = provider.run_with_response(
                probe_id=probe.id,
                rendered_probe=rendered,
                sample_index=sample_index,
                temperature=temperature,
            )
            recorder.add(observation, raw)
    return recorder.flush()
