# ai-citation-probe (working title)

A reproducible measurement tool for AI citations. It does **not** promise to
improve rankings. Its purpose is to make AI visibility measurements auditable:
fixed probes, explicit provider capabilities, stored evidence, public formulas,
and reports that can explain disagreement instead of hiding it behind a score.

## Status

This is the Phase 1 skeleton. The remote GitHub repository and final package
name have not been created yet.

## Design principles

1. Every report references a run manifest with provider profile, model version,
   sampling parameters, time window, probe-set version, and probe-set hash.
2. Provider differences are explicit. A no-search model API is not reported as
   consumer AI-search visibility.
3. Raw response, extracted evidence, and derived metrics are stored separately.
4. Missing or incomparable measurements produce `not_comparable`, never a
   synthetic score.
5. API keys remain in the user's environment; cost and token usage are
   first-class run data.

## Repository layout

```text
docs/architecture.md          # runtime data flow and integration contracts
docs/provider-matrix.md       # provider capability and interpretation matrix
src/ai_citation_probe/        # CLI and core implementation skeleton
configs/providers.example.json
examples/                     # example input/output (added with M2)
tests/                        # unit tests for manifest and metric contracts
```

## Current CLI

```bash
python -m ai_citation_probe --help
python -m ai_citation_probe --version
```

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m ai_citation_probe --version
```

## License

MIT. See [LICENSE](LICENSE).
