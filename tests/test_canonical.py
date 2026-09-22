from ai_citation_probe.canonical import sha256_canonical
import unittest


class CanonicalTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self):
        self.assertEqual(
            sha256_canonical({"a": 1, "b": 2}),
            sha256_canonical({"b": 2, "a": 1}),
        )


if __name__ == "__main__":
    unittest.main()
