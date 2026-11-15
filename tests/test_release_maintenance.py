"""Post-1.0 maintenance must not rewrite the published release or its normative content."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "release"))
import release_candidate
import validate_1_0_engineering as final


class ReleaseMaintenanceTests(unittest.TestCase):
    def test_published_release_manifest_is_immutable(self):
        released = json.loads((ROOT / final.RELEASE_MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(released["tree_digest"], final.RELEASE_1_0_DIGEST)
        self.assertEqual(release_candidate.canonical_digest(released["files"]), final.RELEASE_1_0_DIGEST)

    def test_current_tree_validates_with_maintenance_manifest(self):
        self.assertEqual(final.validate(), [])
        manifest = json.loads((ROOT / final.MAINTENANCE_MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_tree_digest"], final.RELEASE_1_0_DIGEST)
        self.assertFalse(manifest["normative_content_changed"])
        self.assertEqual(manifest["external_review_status"], "pending")

    def test_normative_paths_are_classified(self):
        for rel in ("spec/threat-model.md", "schemas/x.json", "profiles/catalog.json",
                    "fixtures/a/b.json", "adr/0001.md", "reference/x.mjs", "VERSION",
                    "registry/threat-model.json", "registry/cryptographic-algorithms.json"):
            self.assertTrue(final.is_normative(rel), rel)
        for rel in ("registry/prs.json", "registry/requirement-analyses.json",
                    "scripts/crypto_registry.py", "tests/test_x.py",
                    ".github/workflows/validate.yml", "website/build.mjs"):
            self.assertFalse(final.is_normative(rel), rel)

    def test_changed_paths_include_additions_and_removals(self):
        old = {"files": [{"path": "a", "git_blob_sha": "1"}, {"path": "b", "git_blob_sha": "2"}]}
        new = {"files": [{"path": "a", "git_blob_sha": "1"}, {"path": "c", "git_blob_sha": "3"}]}
        self.assertEqual(final.changed_since_release(old, new), ["b", "c"])


if __name__ == "__main__":
    unittest.main()
