import unittest

from ai_citation_probe.probe_set import (
    ProbeSetError,
    parse_probe_set,
    render_probe,
)


def make_probe_set():
    return {
        "meta": {
            "schema": "probe-set/0.1",
            "version": "0.1.1",
            "canonical_hash": "test-hash",
        },
        "defaults": {
            "language": "zh-CN",
            "region": "CN",
            "samples_per_run": 3,
            "temperature": 0,
        },
        "questions": [
            {
                "id": "q-1",
                "text": "{brand} 是什么?",
                "industry": "generic",
                "intent": "navigational",
                "slots": ["brand"],
                "comparable_providers": ["perplexity-sonar"],
                "consumer_surface": "direct",
                "inclusion_reason": "baseline",
                "added_in": "0.1.1",
            }
        ],
    }


class ProbeSetTests(unittest.TestCase):
    def test_parse_probe_set_applies_defaults(self):
        parsed = parse_probe_set(make_probe_set())
        self.assertEqual(parsed.probes[0].language, "zh-CN")
        self.assertEqual(parsed.required_slots, {"brand"})

    def test_duplicate_probe_id_is_rejected(self):
        value = make_probe_set()
        value["questions"].append(dict(value["questions"][0]))
        with self.assertRaises(ProbeSetError):
            parse_probe_set(value)

    def test_render_requires_all_slots(self):
        probe = parse_probe_set(make_probe_set()).probes[0]
        self.assertEqual(render_probe(probe, {"brand": "Example"}), "Example 是什么?")
        with self.assertRaises(ProbeSetError):
            render_probe(probe, {})
