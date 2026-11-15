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
# Published 1.0.0 engineering release (git tag 1.0.0). Its manifest is immutable.
RELEASE_1_0_DIGEST = "sha256:e0b0390cf6c7e36776b7c4d515742cdda68a0edbf35b7b0d53cb3f599d2becb5"
RELEASE_MANIFEST = "release/1.0.0-manifest.json"
MAINTENANCE_MANIFEST = "release/1.0-maintenance-manifest.json"
# Post-release maintenance may change tooling, tests, workflows, website and
# non-normative overlays. It must not change normative 1.0.0 content: that
# requires a new, separately validated release version.
NORMATIVE_PREFIXES = ("spec/", "schemas/", "profiles/", "fixtures/", "adr/", "reference/")
NORMATIVE_FILES = {"VERSION"}
MUTABLE_REGISTRY = {
    "registry/prs.json",
    "registry/roadmap.json",
    "registry/requirement-analyses.json",
    "registry/pr-contract.mjs",
    "registry/pr-contract.test.mjs",
    "registry/PR_FORMAT.md",
}
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
    result.discard(RELEASE_MANIFEST)
    result.discard(MAINTENANCE_MANIFEST)
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


def is_normative(rel):
    if rel in NORMATIVE_FILES or rel.startswith(NORMATIVE_PREFIXES):
        return True
    return rel.startswith("registry/") and rel not in MUTABLE_REGISTRY


def changed_since_release(released, current):
    old = {e["path"]: e["git_blob_sha"] for e in released.get("files", [])}
    new = {e["path"]: e["git_blob_sha"] for e in current["files"]}
    return sorted(p for p in set(old) | set(new) if old.get(p) != new.get(p))


def build_maintenance_manifest():
    """Exact current source tree, bound to (not replacing) the published release."""
    current = build_manifest()
    released = load(RELEASE_MANIFEST)
    return {
        "schema_version": "0.1",
        "release_version": "1.0.0",
        "release_type": "engineering-standard-maintenance",
        "release_tree_digest": RELEASE_1_0_DIGEST,
        "normative_content_changed": False,
        "external_certification": "not-claimed",
        "external_review_status": "pending",
        "individually_authored_requirement_count": current["individually_authored_requirement_count"],
        "normative_requirement_count": current["normative_requirement_count"],
        "changed_since_release": changed_since_release(released, current),
        "file_count": current["file_count"],
        "files": current["files"],
        "tree_digest": current["tree_digest"],
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
    if not (ROOT / RELEASE_MANIFEST).is_file():
        errors.append("missing published 1.0.0 engineering manifest")
        return sorted(set(errors))
    released = load(RELEASE_MANIFEST)
    if (released.get("tree_digest") != RELEASE_1_0_DIGEST
            or release_candidate.canonical_digest(released.get("files", [])) != RELEASE_1_0_DIGEST):
        errors.append("published 1.0.0 engineering manifest was altered")
    if released.get("external_certification") != "not-claimed" or released.get("external_review_status") != "pending":
        errors.append("independent review/certification status misrepresented")
    if not (ROOT / MAINTENANCE_MANIFEST).is_file():
        errors.append("missing post-release maintenance manifest")
    else:
        actual = load(MAINTENANCE_MANIFEST)
        expected = build_maintenance_manifest()
        if actual != expected:
            errors.append("maintenance manifest differs from exact source tree")
        normative = [p for p in expected["changed_since_release"] if is_normative(p)]
        if normative:
            errors.append("normative 1.0.0 content changed without a new release: " + ", ".join(normative))
        if actual.get("external_certification") != "not-claimed" or actual.get("external_review_status") != "pending":
            errors.append("independent review/certification status misrepresented")
    return sorted(set(errors))


if __name__ == "__main__":
    if "--write-maintenance-manifest" in sys.argv[1:]:
        (ROOT / MAINTENANCE_MANIFEST).write_text(
            json.dumps(build_maintenance_manifest(), indent=2) + "\n", encoding="utf-8")
        print("wrote", MAINTENANCE_MANIFEST)
    bad = validate()
    if bad:
        for item in bad:
            print("ERROR:", item)
        raise SystemExit(1)
    artifact = load(MAINTENANCE_MANIFEST)
    print("E2EESA 1.0 published release:", RELEASE_1_0_DIGEST)
    print("Post-release maintenance tree validated:", artifact["tree_digest"],
          "(" + str(len(artifact["changed_since_release"])) + " non-normative paths changed)")
