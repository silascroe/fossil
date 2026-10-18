import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fossil.acquire import AcquisitionError
from fossil.inventory import inspect
from fossil.assessment import assess
from fossil.compare import compare
from test_core import CODE


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_target_only_discovery_searches_source_symbols_and_evaluates_results(self):
        from fossil.discovery import find_candidates
        p = self.root / "target"
        p.mkdir()
        (p / "engine.py").write_text(CODE)
        inv = inspect(p)
        class SearchService:
            def __init__(self): self.queries = []
            def get(self, route):
                self.queries.append(route)
                if route.startswith("/search/code"):
                    return {"items": [{"repository": {"full_name": "original/strata"}, "html_url": "https://github.com/original/strata/blob/main/engine.py"}]}
                return {"items": []}
        service = SearchService()
        leads, trail = find_candidates({"input": "target", "repository": "new/target", "metadata": {}, "inventory": inv}, inv, service)
        self.assertIn("original/strata", leads)
        self.assertTrue(any("decode_fossil_layers" in q for q in service.queries))
        self.assertTrue(any(e["action"] == "code search" for e in trail))

    def test_documented_influence_stays_a_claim_without_source_overlap(self):
        a, b = self.root / "a", self.root / "b"
        a.mkdir(); b.mkdir()
        (a / "README.md").write_text("Inspired by https://github.com/other/idea\n")
        ia, ib = inspect(a), inspect(b)
        result = assess(compare(ia, ib), {"inventory": ia, "git": {}, "metadata": {}}, {"repository": "other/idea", "git": {}})
        self.assertEqual(result["verdict"], "declared_relationship")
        self.assertIn("not independently proven", result["direction"])

    def test_dependency_link_and_unavailable_search_are_not_hidden_successes(self):
        from fossil.discovery import find_candidates
        p = self.root / "target"; p.mkdir()
        (p / "README.md").write_text("Uses https://github.com/psf/requests for HTTP requests\n")
        inv = inspect(p)
        class Blocked:
            def get(self, route): raise AcquisitionError("HTTP 403: rate limit")
        leads, trail = find_candidates({"input": "target", "inventory": inv, "metadata": {}}, inv, Blocked())
        self.assertIn("psf/requests", leads)
        self.assertTrue(any(e.get("status", "").startswith("failed") for e in trail))
        self.assertFalse(any("proven" in r for r in leads["psf/requests"]))

    def test_single_token_insertion_does_not_destroy_all_fingerprints(self):
        a, b = self.root / "a", self.root / "b"; a.mkdir(); b.mkdir()
        (a / "x.py").write_text(CODE)
        (b / "x.py").write_text("insertion\n" + CODE)
        self.assertEqual(compare(inspect(a), inspect(b))["verdict"], "code_overlap")

    def test_api_cache_offline_and_private_token_not_recorded(self):
        from fossil.github import GitHub
        client = GitHub(self.root / "cache")
        payload = {"full_name": "test/repo", "created_at": "2020-01-01T00:00:00Z"}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return json.dumps(payload).encode()
        with patch("fossil.github.urlopen", return_value=Response()) as transport:
            self.assertEqual(client.get("/repos/test/repo"), payload)
            self.assertEqual(transport.call_count, 1)
        offline = GitHub(self.root / "cache", offline=True)
        self.assertEqual(offline.get("/repos/test/repo"), payload)
        with self.assertRaises(AcquisitionError): offline.get("/repos/missing/repo")
        self.assertEqual(offline.trail[0]["status"], "cached")

    def test_ai_suggestions_must_be_github_repositories(self):
        from fossil.ai import parse_suggestions
        answer = '{"candidates": ["https://github.com/original/project", "http://localhost:8000/key", "../../secret", "other/repo"], "notes": "Unverified"}'
        self.assertEqual(parse_suggestions(answer), ["original/project", "other/repo"])


if __name__ == "__main__": unittest.main()
