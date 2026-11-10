#!/usr/bin/env python3
"""Build/validate the source-bound 1.0 engineering release, not certification."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import release_candidate
import requirement_analysis

SOURCE_RC2_DIGEST = "sha256:fb87aac31bde869934fb905c698a3fdd11fed2164add0d4e4a8a4f87d0835256"
ADDITIONAL_FILES = [
    "AGENTS.md",
    "release/0.9.0-rc.2-manifest.json",
    "release/1.0.0-RELEASE-NOTES.md",
    "release/engineering_1_0.py",
    "release/validate_1_0_engineering.py",
    "website/app.js",
    "website/build.mjs",
    "website/check.mjs",
    "website/smoke.mjs",
    "website/markdown.mjs",
    "website/styles.css",
    "website/docs.css",
    "website/icon.svg",
]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def frozen_paths():
    policy = load("registry/release-candidate.json")
    result = set(release_candidate.frozen_paths(ROOT, policy))
    review = ROOT / "review"
    if review.is_dir():
        result.update(
            p.relative_to(ROOT).as_posix()
            for p in review.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )
    result.update(ADDITIONAL_FILES)
    result.discard("release/1.0.0-manifest.json")
    for rel in result:
        if not (ROOT / rel).is_file():
            raise ValueError("missing engineering release artifact: " + rel)
    return sorted(result)


def build_manifest():
    entries = []
    for rel in frozen_paths():
        data = (ROOT / rel).read_bytes()
        entries.append({
            "path": rel,
            "size": len(data),
            "git_blob_sha": release_candidate.git_blob_sha(data),
        })
    analysis = requirement_analysis.validate_repository(ROOT)
    return {
        "schema_version": "0.1",
        "release_version": "1.0.0",
        "release_type": "engineering-standard",
        "source_rc2_digest": SOURCE_RC2_DIGEST,
        "external_certification": "not-claimed",
        "external_review_status": "pending",
        "individually_authored_requirement_count": analysis["authored"],
        "normative_requirement_count": analysis["total"],
        "file_count": len(entries),
        "files": entries,
        "tree_digest": release_candidate.canonical_digest(entries),
    }


def validate():
    errors = []
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "1.0.0":
        errors.append("VERSION must equal 1.0.0")
    rc2 = load("release/0.9.0-rc.2-manifest.json")
    if rc2.get("tree_digest") != SOURCE_RC2_DIGEST:
        errors.append("historical rc.2 source digest changed")
    if release_candidate.canonical_digest(rc2.get("files", [])) != SOURCE_RC2_DIGEST:
        errors.append("historical rc.2 manifest bytes changed")
    policy = load("registry/release-candidate.json")
    if policy.get("release_version") != "0.9.0-rc.2":
        errors.append("historical rc.2 policy changed")
    errors.extend(release_candidate.validate_historical_candidates(ROOT, policy))
    for rel in ("profiles/catalog.json", "registry/cryptographic-algorithms.json",
                "registry/integration-contracts.json"):
        if load(rel).get("standard_version") != "1.0.0":
            errors.append(rel + " retains an unfinished standard basis")
    analysis = requirement_analysis.validate_repository(ROOT)
    errors.extend("analysis: " + x for x in analysis["errors"])
    if analysis["authored"] > analysis["total"] or analysis["independently_authenticated_reviewed"] > analysis["review_recorded"]:
        errors.append("impossible requirement provenance counts")
    if (ROOT / "INDEPENDENT-REVIEW-COMPLETE.md").exists():
        errors.append("no authenticated independent-review completion exists for this engineering release")
    if not (ROOT / "release/1.0.0-manifest.json").is_file():
        errors.append("missing final content-addressed engineering manifest")
    else:
        actual = load("release/1.0.0-manifest.json")
        expected = build_manifest()
        if actual != expected:
            errors.append("engineering release manifest differs from exact source tree")
        if actual.get("external_certification") != "not-claimed" or actual.get("external_review_status") != "pending":
            errors.append("independent review/certification status misrepresented")
    return sorted(set(errors))


if __name__ == "__main__":
    bad = validate()
    if bad:
        for item in bad:
            print("ERROR:", item)
        raise SystemExit(1)
    artifact = load("release/1.0.0-manifest.json")
    print("E2EESA 1.0 engineering source manifest validated:", artifact["tree_digest"])
