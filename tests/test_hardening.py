import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from fossil.acquire import AcquisitionError, extract_zip, repo_name
from fossil.case import investigate, replay
from fossil.inventory import inspect
from fossil.assessment import assess
from fossil.compare import compare
from test_core import CODE


class HardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_zip_with_large_asset_skips_asset_but_keeps_code(self):
        archive = self.root / "repo.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("project/engine.py", CODE)
            z.writestr("project/image.png", b"x" * 1_000_001)
        warnings = extract_zip(archive, self.root / "out")
        self.assertTrue((self.root / "out/project/engine.py").is_file())
        self.assertFalse((self.root / "out/project/image.png").exists())
        self.assertTrue(any("limit" in w.lower() for w in warnings))

    def test_documentary_claim_must_refer_to_subject_not_a_list_of_links(self):
        a, b = self.root / "a", self.root / "b"; a.mkdir(); b.mkdir()
        (a / "README.md").write_text("A fork of [Real](https://github.com/upstream/real). Uses [HTTP](https://github.com/psf/requests).\n")
        (a / "engine.py").write_text(CODE); (b / "engine.py").write_text(CODE)
        ia, ib = inspect(a), inspect(b)
        result = assess(compare(ia, ib), {"inventory": ia, "git": {}, "metadata": {}}, {"repository": "psf/requests", "git": {}})
        self.assertEqual(result["verdict"], "code_overlap")
        self.assertEqual(result["documentary"], [])

    def test_snapshot_tampering_fails_replay(self):
        a = self.root / "a"; a.mkdir(); (a / "engine.py").write_text(CODE)
        case = self.root / "case"
        investigate(str(a), [], case)
        (case / "snapshots/target/engine.py").write_text("tampered")
        with self.assertRaisesRegex(AcquisitionError, "integrity"):
            replay(case)

    def test_followup_preserves_old_case_and_records_changes(self):
        a, b = self.root / "a", self.root / "b"; a.mkdir(); b.mkdir()
        (a / "engine.py").write_text(CODE); (b / "engine.py").write_text(CODE)
        first, second = self.root / "first", self.root / "second"
        c1 = investigate(str(a), [str(b)], first)
        original = (first / "case.json").read_bytes()
        (a / "engine.py").write_text("print('different')")
        c2 = investigate(str(a), [], second, follow_up=first)
        self.assertEqual((first / "case.json").read_bytes(), original)
        self.assertEqual(c2["previous_case"]["id"], c1["id"])
        self.assertEqual(c2["comparisons"][0]["verdict"], "not_established")
        self.assertTrue(c2["changes"]["target_changed"])
        self.assertEqual(c2["changes"]["verdict_changes"][0]["before"], "code_overlap")

    def test_ai_roundtrip_uses_evidence_only_and_retains_audit_without_key(self):
        from fossil.ai import Advisor
        env = {"FOSSIL_AI_KEY": "secret-never-save", "FOSSIL_AI_MODEL": "test-model", "FOSSIL_AI_BASE_URL": "https://provider.invalid/v1"}
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return json.dumps({"choices":[{"message":{"content":'{"candidates":["source/original"]}'}}]}).encode()
        with patch.dict(os.environ, env), patch("fossil.ai.urlopen", return_value=Response()):
            advisor = Advisor()
            a = self.root / "a"; a.mkdir(); (a / "engine.py").write_text(CODE)
            case = investigate(str(a), [], self.root / "case", ai=advisor)
        self.assertEqual(len(case["ai_audit"]), 1)
        self.assertNotIn("secret-never-save", json.dumps(case))
        self.assertIn("input", case["ai_audit"][0])

    def test_github_urls_reject_other_hosts_and_traversal(self):
        self.assertIsNone(repo_name("https://evil.invalid/owner/repo"))
        self.assertIsNone(repo_name("../secret"))
        self.assertEqual(repo_name("https://github.com/good/repo.git"), "good/repo")

    def test_fork_metadata_and_shared_history_are_separate_evidence(self):
        a = {"files": [], "references": [], "dependencies": []}
        c = {"repository": "upstream/repo", "git": {"commits": [{"sha": "a"*40}]}}
        t = {"inventory": a, "metadata": {"parent": {"full_name": "upstream/repo"}}, "git": {"commits": [{"sha": "a"*40}]}}
        result = assess(compare(a, a), t, c)
        self.assertEqual(result["verdict"], "declared_fork")
        self.assertEqual(result["shared_commits"], ["a"*40])
        self.assertEqual(result["matches"], [])


if __name__ == "__main__": unittest.main()

class LocalSafetyTests(unittest.TestCase):
    def test_local_git_fsmonitor_is_not_executed(self):
        from fossil.acquire import history
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q',str(p)],check=True)
            (p/'a.py').write_text('pass\n')
            subprocess.run(['git','-C',str(p),'add','.'],check=True)
            subprocess.run(['git','-C',str(p),'-c','user.name=Test','-c','user.email=t@example.invalid','commit','-qm','init'],check=True)
            script=p/'hook.sh'; marker=p/'executed'
            script.write_text('#!/bin/sh\ntouch "'+str(marker)+'"\n');script.chmod(0o755)
            subprocess.run(['git','-C',str(p),'config','core.fsmonitor',str(script)],check=True)
            history(p)
            self.assertFalse(marker.exists())

    def test_local_case_excludes_credentials_and_gitignored_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source';p.mkdir()
            subprocess.run(['git','init','-q',str(p)],check=True)
            (p/'.env').write_text('TOKEN=secret')
            (p/'.npmrc').write_text('authToken=secret')
            (p/'.gitignore').write_text('private.txt\n')
            (p/'private.txt').write_text('secret')
            (p/'engine.py').write_text(CODE)
            c=investigate(str(p),[],Path(d)/'case')
            paths=[f['path'] for f in c['target']['inventory']['files']]
            self.assertIn('engine.py',paths)
            self.assertNotIn('.env',paths)
            self.assertNotIn('.npmrc',paths)
            self.assertNotIn('private.txt',paths)
