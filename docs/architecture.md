# Architecture

## Data flow

```text
probe-set.yaml + provider profile
        ↓ validate and canonical hash
     RunManifest
        ↓ render slots and execute samples
   Provider adapters
        ↓ raw response
   Evidence extractor
        ↓ ProviderObservation
   Consistency metrics
        ↓ JSONL + CSV + HTML
       Report
```

## Contracts

- Probe set: versioned YAML owned by Phase 2. It carries semantic metadata and
  declares which providers are comparable for each probe. Its hash is computed
  from the **parsed structure** after removing `meta.canonical_hash`; YAML
  formatting and comments are irrelevant. The hash input is bare canonical
  JSON bytes with no trailing newline.
- Run manifest: immutable record created before the first provider call. It
  stores the probe-set **version and canonical hash as a pair**, plus provider
  profile hash, model versions, sampling count, temperature, and time window.
- Raw responses: append-only files addressed by `raw_response_uri`.
- Evidence: provider citations and extracted brand mentions, separate from
  model prose.
- Metrics: only the public functions in `metrics.py`; report rendering cannot
  invent alternative formulas. Cross-provider URL similarity reports both
  `jaccard_union` (optimistic coverage) and `jaccard_intersect` (paired
  samples). Comparisons across probe-set versions use only the intersection of
  question IDs.
- Costs: token/cost data accompanies every observation when the provider
  exposes it.

## Error and comparability policy

Transport errors, refusals, missing citation metadata, and provider-specific
features are represented explicitly. Reports may show `not_comparable`, but
they must not interpolate a plausible value or merge incompatible search modes.

## M1 acceptance

1. Probe-set loading fails closed when schema, required fields, IDs, or
   `canonical_hash` are invalid or mismatched.
2. Manifest construction records probe-set version/hash, samples, temperature,
   time, and provider-profile hash.
3. The first provider transport (Perplexity sonar) executes a fixed probe set
   and emits JSONL observations.
4. Each observation has model version, sample index, raw response URI, status,
   citations, token usage, optional cost, and latency.
5. No API key is written into the manifest, observations, report, or logs.

Remaining for M1: integration smoke against a live key, explicit report-side
surface grouping, and the PR-move of authoritative protocol files into this
repository.
