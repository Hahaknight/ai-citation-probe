# ai-citation-probe

A reproducible measurement tool for AI citations. It does **not** promise to
improve rankings. Its purpose is to make AI visibility measurements auditable:
fixed probes, explicit provider capabilities, stored evidence, public formulas,
and reports that can explain disagreement instead of hiding it behind a score.

## Status

The Phase 1 skeleton is public. The M1 measurement core now validates the
versioned probe-set protocol and runs Perplexity sonar with raw response,
citation, token, cost, and latency capture.

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
src/ai_citation_probe/        # CLI and M1 measurement core
configs/providers.example.json
examples/                     # example input/output (added with M2)
tests/                        # unit tests for manifest and metric contracts
```

## Current CLI

```bash
PYTHONPATH=src python -m ai_citation_probe validate --probe-set probe-set.yaml
PYTHONPATH=src python -m ai_citation_probe run \
  --probe-set probe-set.yaml \
  --profiles configs/providers.example.json \
  --provider perplexity-sonar \
  --run-id demo-001 \
  --slot brand=Example \
  --output-dir runs/demo-001
PYTHONPATH=src python -m ai_citation_probe --version
```

Perplexity runs read `PERPLEXITY_API_KEY` from the environment. API keys are
never written to manifests, observations, raw responses, or logs.

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m ai_citation_probe --version
```

## License

MIT. See [LICENSE](LICENSE).
