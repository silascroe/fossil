import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


# This distinctive algorithm stands in for application code in unit tests only.
CODE = '''def decode_fossil_layers(records, epoch_offset):
    reconstructed_strata = []
    previous_boundary = epoch_offset
    for layer_index, sediment_record in enumerate(records):
        observed_boundary = sediment_record.get("boundary", previous_boundary)
        mineral_signature = sediment_record.get("mineral", "unknown")
        corrected_boundary = max(observed_boundary, previous_boundary)
        layer_duration = corrected_boundary - previous_boundary
        reconstructed_strata.append({
            "ordinal": layer_index,
            "signature": mineral_signature,
            "duration": layer_duration,
            "boundary": corrected_boundary,
        })
        previous_boundary = corrected_boundary
    return sorted(reconstructed_strata, key=lambda layer: layer["boundary"])
'''


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def project(self, name, code=CODE):
        p = self.root / name
        p.mkdir()
        (p / "engine.py").write_text(code)
        return p

    def test_identical_code_has_specific_line_evidence_but_no_direction(self):
        from fossil.inventory import inspect
        from fossil.compare import compare
        a, b = self.project("a"), self.project("b")
        result = compare(inspect(a), inspect(b))
        self.assertEqual(result["verdict"], "code_overlap")
        self.assertEqual(result["direction"], "undetermined")
        self.assertEqual(result["matches"][0]["kind"], "exact_source")
        self.assertGreater(result["matches"][0]["tokens"], 80)
        self.assertIn("decode_fossil_layers", result["matches"][0]["example"])
        self.assertEqual(result["matches"][0]["target_lines"][0], 1)

    def test_modified_copy_is_found_across_different_filenames(self):
        from fossil.inventory import inspect
        from fossil.compare import compare
        a, b = self.project("a"), self.project("b", CODE.replace("sorted(reconstructed_strata", "list(reconstructed_strata"))
        (b / "engine.py").rename(b / "renamed.py")
        result = compare(inspect(a), inspect(b))
        self.assertEqual(result["verdict"], "code_overlap")
        self.assertGreater(result["matches"][0]["tokens"], 80)

    def test_conventions_dependencies_and_licenses_do_not_establish_ancestry(self):
        from fossil.inventory import inspect
        from fossil.compare import compare
        a, b = self.project("a", "def main():\n    print('Hello world')\n"), self.project("b", "def main():\n    print('Hello world')\n")
        for p in (a, b):
            (p / "requirements.txt").write_text("requests==2.32.0\n")
            (p / "LICENSE").write_text("MIT License\nPermission is hereby granted")
        result = compare(inspect(a), inspect(b))
        self.assertEqual(result["verdict"], "not_established")
        self.assertEqual(result["matches"], [])
        self.assertIn("requests", result["shared_dependencies"])

    def test_vendored_overlap_is_not_project_ancestry(self):
        from fossil.inventory import inspect
        from fossil.compare import compare
        a, b = self.project("a", "print('app one')"), self.project("b", "print('app two')")
        for p in (a, b):
            (p / "vendor").mkdir()
            (p / "vendor" / "lib.py").write_text(CODE)
        result = compare(inspect(a), inspect(b))
        self.assertEqual(result["verdict"], "component_overlap")
        self.assertTrue(result["matches"][0]["context"])

    def test_zip_traversal_is_rejected_and_symlinks_not_followed(self):
        from fossil.acquire import extract_zip, AcquisitionError
        z = self.root / "bad.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("../escape.py", CODE)
        with self.assertRaises(AcquisitionError):
            extract_zip(z, self.root / "out")
        self.assertFalse((self.root / "escape.py").exists())
        from fossil.inventory import inspect
        p = self.project("a")
        try:
            (p / "link.py").symlink_to(p / "engine.py")
        except OSError:
            self.skipTest("creating symlinks needs extra privileges on this platform")
        self.assertEqual(len(inspect(p)["files"]), 1)

    def test_inventory_order_is_case_sensitive_and_component_wise_on_every_platform(self):
        # The snapshot digest depends on file order; cases must replay on any OS.
        from fossil.inventory import inspect
        p = self.root / "order"
        (p / "utils").mkdir(parents=True)
        for name in ("a.py", "B.py", "utils.md", "utils/x.py"):
            (p / name).write_text("pass\n")
        self.assertEqual([f["path"] for f in inspect(p)["files"]], ["B.py", "a.py", "utils/x.py", "utils.md"])

    def test_history_reads_utf8_case_ledgers_regardless_of_locale(self):
        import io
        from contextlib import redirect_stdout
        from fossil.cli import main
        case = self.root / "cases" / "one"
        case.mkdir(parents=True)
        ledger = {"created_at": "2026-11-01T00:00:00+00:00", "id": "abc", "target": {"input": "Łódź"}}
        (case / "case.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["history", "--cases", str(self.root / "cases")]), 0)
        self.assertIn("Łódź", out.getvalue())

    def test_cli_preserves_replayable_case_and_local_working_tree(self):
        a, b = self.project("a"), self.project("b")
        subprocess.run(["git", "init", "-q", str(a)], check=True)
        subprocess.run(["git", "-C", str(a), "add", "."], check=True)
        subprocess.run(["git", "-C", str(a), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "initial"], check=True)
        (a / "note.txt").write_text("uncommitted evidence")
        case = self.root / "case"
        run = subprocess.run(["python", "-m", "fossil", "investigate", str(a), "--candidate", str(b), "--no-discovery", "--case", str(case)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        ledger = json.loads((case / "case.json").read_text())
        self.assertEqual(ledger["comparisons"][0]["verdict"], "code_overlap")
        self.assertTrue(ledger["target"]["git"]["dirty"])
        self.assertTrue((case / "report.md").is_file())
        replay = subprocess.run(["python", "-m", "fossil", "replay", str(case)], capture_output=True, text=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertIn("verified", replay.stdout.lower())


if __name__ == "__main__":
    unittest.main()
