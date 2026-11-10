# E2EESA 0.9 Release Candidate

**Status:** Current frozen engineering candidate `0.9.0-rc.2`; original `0.9.0-rc.1` remains immutable. Independent review remains pending.

E2EESA 0.9 is the first frozen release candidate of the complete architecture standard.

## Release identity

The release version is `0.9.0-rc.1`.

The existing machine-readable profile and registry basis remains `0.1.0-dev` during the 0.9 review cycle. The release manifest binds that exact basis by digest rather than silently rewriting profile, fixture, or evidence identities that have already been validated.

PR 50 is responsible for the deliberate 1.0 version transition after independent review fixes are incorporated.

## Frozen release surface

The candidate manifest freezes:

- normative and supporting specification documents;
- schemas;
- registries;
- profile catalog;
- architecture decision records;
- reference SQL/material;
- repository validation and conformance scripts;
- reference fixtures;
- conformance tests; and
- the validation workflow.

Generated caches, Git metadata, and the release manifest itself are excluded from its own content digest.

## Candidate completeness gates

A 0.9 candidate is valid only when:

- repository validation passes;
- all current catalog profiles are represented by the PR 43 reference-fixture manifest;
- every production-positive profile is covered by the PR 44 interoperability corpus;
- every unordered pair of production-positive profiles is present exactly once in the PR 44 pair report;
- PR 46 standards-crosswalk coverage is 100%;
- PR 47 security-rationale coverage is 100%;
- all six PR 45 integration contracts validate;
- the profile catalog, cryptographic registry, conformance registry, promotion registry, migration registry, and integration registry validate;
- all files in the frozen surface match their stored Git blob object IDs and byte sizes;
- no unexpected frozen file is added or removed; and
- the release version and basis version match the release registry.

## End-to-end candidate suite

The release-candidate checker composes the existing validators rather than creating weaker duplicate logic.

It checks:

- profile/configuration resolution;
- cryptographic registry invariants;
- conformance policy/state;
- reference fixture coverage;
- cross-profile compatibility/interoperability coverage;
- integration contracts;
- standards crosswalk;
- security rationale corpus; and
- release manifest integrity.

The normal CI workflow continues to run every unit test and seeded adversarial reference check after repository validation.

## Candidate freeze semantics

A change to any frozen file changes its Git blob object ID and therefore the SHA-256 digest of the ordered release manifest, invalidating the candidate until the manifest is intentionally regenerated.

PR 49 may change frozen material only to incorporate documented independent expert-review findings.

Any PR 49 change therefore produces a new candidate-manifest digest even if the release label remains in the 0.9 review line.

## Review boundary

The 0.9 candidate is not E2EESA 1.0.

It is specifically intended for independent cryptographic, protocol, implementation, conformance, accessibility, and standards review before the 1.0 release decision.

The candidate status does not by itself certify any product.

## Authoritative files

- `VERSION`
- `registry/release-candidate.json`
- `schemas/release-candidate.schema.json`
- `release/0.9.0-rc.1-manifest.json`
- `scripts/release_candidate.py`
- `tests/test_release_candidate.py`

## Audit remediation and historical candidate preservation

The rc.1 manifest and archived source bytes remain immutable. The active development manifest is a distinct artifact for rc.2 development, regenerated after each change and checked against the complete active release surface. Archived bytes are verified without extracting archive paths or requiring Git history. A development manifest is not a candidate freeze, independent review, or production certification.

## Current rc.2 candidate and limits

The current frozen source tree is recorded in `release/0.9.0-rc.2-manifest.json`, while the original rc.1 archive remains byte-verified. `registry/audit-remediation.json` records normative/reference implementation and regression-test evidence, not evidence of certified hardware, implemented product integrations, or independent audit. The optional AUD-16 research track and incomplete AUD-22 individual requirement analysis remain explicitly pending (21 of 1,055 authored). External review does not block engineering release by owner policy; failed required tests and actual vulnerabilities do. No product certification is implied.
