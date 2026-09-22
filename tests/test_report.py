import tempfile
import unittest
from pathlib import Path

from ai_citation_probe.report import (
    load_observations,
    render_csv,
    render_html,
    summarize_observations,
)


class ReportTests(unittest.TestCase):
    def test_load_observations_tolerates_truncated_final_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observations.jsonl"
            path.write_text(
                '{"probe_id":"q-1"}\n{"probe_id":"q-2"',
                encoding="utf-8",
            )
            loaded = load_observations(path)

        self.assertEqual(len(loaded.observations), 1)
        self.assertTrue(loaded.warnings)

    def test_summary_and_reports_group_by_surface(self):
        observations = [
            {
                "probe_id": "q-1",
                "provider_id": "search",
                "status": "ok",
                "citations": [{"url": "https://example.com"}],
                "evidence_category": "brand_with_citation",
                "cost_usd": 0.02,
                "token_usage": {"total_tokens": 10},
                "latency_ms": 100,
            },
            {
                "probe_id": "q-1",
                "provider_id": "no-search",
                "status": "error",
                "citations": [],
                "evidence_category": "refused_or_unsearchable",
                "latency_ms": 50.5,
            },
        ]
        profiles = {
            "search": {"surface_equivalence": "direct"},
            "no-search": {"surface_equivalence": "no"},
        }
        rows = summarize_observations(observations, profiles)
        self.assertEqual(len(rows), 2)
        surfaces = {row["provider_id"]: row["consumer_surface"] for row in rows}
        self.assertEqual(surfaces["search"], "direct")
        self.assertEqual(surfaces["no-search"], "no")
        latencies = {
            row["provider_id"]: row["mean_latency_ms"] for row in rows
        }
        self.assertEqual(latencies["no-search"], 50.5)
        self.assertEqual(latencies["search"], 100)

        with tempfile.TemporaryDirectory() as directory:
            csv_path = render_csv(rows, Path(directory) / "summary.csv")
            html_path = render_html(
                manifest={
                    "run_id": "r",
                    "probe_set_version": "0.1.1",
                    "probe_set_hash": "h",
                },
                rows=rows,
                warnings=["ignored truncated final observation"],
                path=Path(directory) / "report.html",
            )
            csv_text = csv_path.read_text(encoding="utf-8")
            html_text = html_path.read_text(encoding="utf-8")

        self.assertIn("search", csv_text)
        self.assertIn("Model capability baseline", html_text)
        self.assertIn("ignored truncated final observation", html_text)
