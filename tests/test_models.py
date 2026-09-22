import unittest
from datetime import datetime, timezone

from ai_citation_probe.models import RunManifest


def make_manifest(**overrides):
    values = {
        "schema": "run-manifest/0.1",
        "run_id": "run-1",
        "created_at": datetime.now(timezone.utc),
        "probe_set_version": "0.1.0",
        "probe_set_hash": "hash",
        "providers": (),
        "samples_per_probe": 2,
        "temperature": 0,
        "provider_profile_hash": "hash",
    }
    values.update(overrides)
    return RunManifest(**values)


class ManifestTests(unittest.TestCase):
    def test_manifest_requires_probe_set_version_and_hash(self):
        with self.assertRaises(ValueError):
            make_manifest(probe_set_version="")

        with self.assertRaises(ValueError):
            make_manifest(probe_set_hash="")

    def test_manifest_requires_at_least_two_samples(self):
        with self.assertRaises(ValueError):
            make_manifest(samples_per_probe=1)


if __name__ == "__main__":
    unittest.main()
