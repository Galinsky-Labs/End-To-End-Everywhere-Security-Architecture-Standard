#!/usr/bin/env python3
"""Promote the tested rc.2 candidate to an owner-authorized 1.0 engineering standard.

This does NOT claim independent human review or downstream product certification.
The original rc.1 archive and rc.2 manifest/policy remain unchanged.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "release"))
import standards_crosswalk
import requirement_analysis
import validate_1_0_engineering as final

OLD = "0.1.0-dev"
NEW = "1.0.0"
SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml", ".mjs", ".txt", ".toml", ".sql"}
EXCLUSIONS = {
    "registry/release-candidate.json",
    "registry/requirement-analyses.json",
    "spec/release-candidate.md",
    "tests/test_release_candidate.py",
}
ROOTS = [".github/workflows", "adr", "fixtures", "profiles", "reference",
         "registry", "schemas", "scripts", "spec", "tests"]


def write_json(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")


def scan_changes():
    touched = []
    for relroot in ROOTS:
        for path in sorted((ROOT / relroot).rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative in EXCLUSIONS:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if OLD in content:
                touched.append((relative, content))
    return touched


def adjust_active_validator():
    path = ROOT / "scripts/validate_repo.py"
    content = path.read_text(encoding="utf-8")
    pattern = r"^(CANDIDATE_VERSION = re.compile.+)$"
    content, changes = re.subn(
        pattern, lambda m: m.group(1) + "\n" + 'STABLE_VERSION = re.compile(r"^1\\.0\\.0$")',
        content, count=1, flags=re.MULTILINE,
    )
    if changes != 1:
        raise ValueError("VERSION validator marker missing")
    before = "DEV_VERSION.fullmatch(version) or CANDIDATE_VERSION.fullmatch(version)"
    after = before + " or STABLE_VERSION.fullmatch(version)"
    if before not in content:
        raise ValueError("VERSION validation expression missing")
    content = content.replace(before, after)
    content = content.replace(
        "VERSION must use x.y.z-dev or the 0.9.0-rc.N candidate line before 1.0",
        "VERSION must use development, candidate, or the 1.0.0 engineering release",
    )
    before = ('    errors.extend(\n'
              '        "release candidate: " + error\n'
              '        for error in release_candidate.validate_release(root)\n'
              '    )')
    after = ('    if (root / "VERSION").is_file() and '
             '(root / "VERSION").read_text(encoding="utf-8").strip() != "1.0.0":\n'
             '        errors.extend(\n'
             '            "release candidate: " + error\n'
             '            for error in release_candidate.validate_release(root)\n'
             '        )')
    if before not in content:
        raise ValueError("legacy candidate release gate missing")
    content = content.replace(before, after)
    path.write_text(content, encoding="utf-8")


def adjust_historical_candidate_tests():
    path = ROOT / "tests/test_release_candidate.py"
    content = path.read_text(encoding="utf-8")
    pairs = [
        ('self.assertEqual((ROOT/"VERSION").read_text(encoding="utf-8").strip(),"0.9.0-rc.2")',
         'self.assertEqual((ROOT/"VERSION").read_text(encoding="utf-8").strip(),"1.0.0")'),
        ('self.assertEqual(self.load("profiles/catalog.json")["standard_version"],"0.1.0-dev")',
         'self.assertEqual(self.load("profiles/catalog.json")["standard_version"],"1.0.0")'),
        ('self.assertEqual(self.load("registry/cryptographic-algorithms.json")["standard_version"],"0.1.0-dev")',
         'self.assertEqual(self.load("registry/cryptographic-algorithms.json")["standard_version"],"1.0.0")'),
        ('self.assertEqual(self.load("registry/integration-contracts.json")["standard_version"],"0.1.0-dev")',
         'self.assertEqual(self.load("registry/integration-contracts.json")["standard_version"],"1.0.0")'),
        ('self.assertEqual(release_candidate.validate_release(ROOT),[])',
         'self.assertEqual(release_candidate.validate_historical_candidates(ROOT,self.load("registry/release-candidate.json")),[])'),
        ('self.assertEqual(stored,generated)',
         'self.assertEqual(stored["tree_digest"],release_candidate.canonical_digest(stored["files"]))'),
    ]
    for old, new in pairs:
        if old not in content:
            raise ValueError("historical release test expression missing: " + old)
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")


def amend_readme():
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    start = "## Current status\n"
    end = "\n## End-to-End Everywhere progress"
    if start not in text or end not in text:
        raise ValueError("README current-status section missing")
    prefix, body = text.split(start, 1)
    _previous, following = body.split(end, 1)
    replacement = (
        "## Current status\n\n"
        "**E2EESA 1.0.0 is the owner-authorized stable engineering edition of the "
        "implementation-neutral architecture standard.** It is published from a "
        "validated, immutable rc.2 source candidate. Conformance to the standard "
        "requires independent scoped product evidence; this publication alone "
        "does not certify any product. External expert review remains pending "
        "and is not falsely reported as complete.\n\n"
        "Audit v2 normative/reference-tooling work is recorded in "
        "registry/audit-remediation.json. Optional PQ MLS research and "
        "completion of individual requirement-level rationales are tracked "
        "separately; at the source rc.2 freeze, 21 of 1,055 paragraphs had "
        "individual analysis and no externally authenticated review. "
        "Failed security tests or demonstrable vulnerabilities remain genuine "
        "reasons to withhold affected conformance claims.\n"
    )
    path.write_text(prefix + replacement + end + following, encoding="utf-8")


def amend_website():
    path = ROOT / "website/build.mjs"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "This engineering release candidate has not completed independent expert review and does not confer product certification or approval.",
        "E2EESA 1.0.0 is an engineering standard; independent expert review remains pending and publication does not certify a product.",
    )
    path.write_text(text, encoding="utf-8")


def apply():
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "0.9.0-rc.2":
        raise ValueError("promotion requires source-frozen 0.9.0-rc.2")
    old_manifest = json.loads((ROOT / "release/0.9.0-rc.2-manifest.json").read_text())
    if old_manifest["tree_digest"] != final.SOURCE_RC2_DIGEST:
        raise ValueError("source candidate not the approved exact rc.2 tree")
    old_analyses = json.loads((ROOT / "registry/requirement-analyses.json").read_text())
    previous = {}
    for row in old_analyses["records"]:
        doc = row["document_path"]
        if doc not in previous:
            previous[doc] = standards_crosswalk.extract_requirements_from_text(
                doc, (ROOT / doc).read_text(encoding="utf-8")
            )
    touched = scan_changes()
    for rel, content in touched:
        (ROOT / rel).write_text(content.replace(OLD, NEW), encoding="utf-8")
    adjust_active_validator()
    adjust_historical_candidate_tests()
    new_basis = requirement_analysis.source_basis(ROOT)
    new_lookup = {}
    for doc, rows in previous.items():
        current = standards_crosswalk.extract_requirements_from_text(
            doc, (ROOT / doc).read_text(encoding="utf-8")
        )
        if len(current) != len(rows):
            raise ValueError("source requirement cardinality changed in " + doc)
        new_lookup.update({a["requirement_id"]: b for a, b in zip(rows, current)})
    for row in old_analyses["records"]:
        item = new_lookup.get(row["requirement_id"])
        if item is None:
            raise ValueError("orphaned requirement during version promotion")
        row["requirement_id"] = item["requirement_id"]
        row["text_digest"] = item["text_digest"]
        if row["dependencies"]:
            raise ValueError("version promotion needs explicit dependency review")
        row["context_digest"] = requirement_analysis.current_context_digest(
            row, item, [], new_basis
        )
    write_json("registry/requirement-analyses.json", old_analyses)
    (ROOT / "VERSION").write_text("1.0.0\n", encoding="utf-8")
    workflow = ROOT / ".github/workflows/validate.yml"
    w = workflow.read_text(encoding="utf-8")
    needle = "      - name: Validate 0.9 candidate freeze\n        run: python scripts/release_candidate.py"
    if needle not in w:
        raise ValueError("candidate CI step changed")
    w = w.replace(needle, "      - name: Validate 1.0 engineering source freeze\n        run: python release/validate_1_0_engineering.py")
    workflow.write_text(w, encoding="utf-8")
    amend_readme()
    amend_website()
    notes = (
        "# End-to-End Everywhere Security Architecture Standard 1.0.0\n\n"
        "Engineering release of the normative architecture, schemas, profiles, "
        "reference conformance tooling and source-backed documentation.\n\n"
        "The source candidate is rc.2, commit "
        "8d2b4d38f5f171660a39ee30791aad7e58a09709, tree digest "
        + final.SOURCE_RC2_DIGEST + ". Original rc.1 evidence remains preserved.\n\n"
        "## Scope and limitations\n\n"
        "- **No independent human certification is claimed.** External expert review remains pending.\n"
        "- This version does not certify a product, actual E2EE provider, secure hardware or production implementation.\n"
        "- Audit v2 normative/reference implementations have source and regression evidence; "
        "these are not substitutes for independently observed product behavior.\n"
        "- Individual rationale coverage is 21 of 1,055 normative requirements, "
        "with further analysis tracked openly. Optional PQ MLS research is not production-approved.\n"
        "- Deployment conformance requires exact scoped source, build, data-flow, "
        "cryptographic-provider and runtime evidence under the chosen profile.\n"
    )
    (ROOT / "release/1.0.0-RELEASE-NOTES.md").write_text(notes, encoding="utf-8")
    result = requirement_analysis.validate_repository(ROOT)
    if result["errors"]:
        raise ValueError("post-promotion requirement provenance: " + "; ".join(result["errors"]))
    if result["authored"] != len(old_analyses["records"]):
        raise ValueError("lost authored requirement entries in promotion")
    manifest = final.build_manifest()
    write_json("release/1.0.0-manifest.json", manifest)
    errors = final.validate()
    if errors:
        raise ValueError("engineering release validation failed: " + "; ".join(errors))
    print("Promoted", len(touched), "versioned files. Final digest:", manifest["tree_digest"])
    print("Individual analysis:", result["authored"], "of", result["total"])
    print("Independent review: pending; certification not claimed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", required=True)
    parser.parse_args()
    apply()
