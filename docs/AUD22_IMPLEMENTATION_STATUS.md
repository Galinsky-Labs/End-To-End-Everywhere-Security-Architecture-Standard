# AUD-22 individual requirement analysis status

`registry/requirement-analyses.json` holds individually authored, source-bound analyses of normative paragraphs extracted by `scripts/standards_crosswalk.py`. Each record is bound to the exact requirement text digest and to the current threat, property, external-standard and crosswalk registries; any change to these makes the record stale and fails CI.

The authoritative current count is printed by `python scripts/requirement_analysis.py` (`authored` out of `total`). Records are AI-assisted authorship (`author_id: galinsky-labs-ai-assisted`); each rationale was written against the specific requirement text, not projected from a document-wide rationale. `review` is `null` for every record: **no independent human review has occurred**, and none is claimed.

Coverage added after the 1.0.0 release is a non-normative overlay tracked by `release/1.0-maintenance-manifest.json`; the published 1.0.0 manifest and normative text are unchanged.

| Batch | Documents | Records |
| --- | --- | --- |
| rc.2 freeze | key-change state machine, hardware recovery budgets, pairwise prekey lifecycle, push provider privacy | 21 |
| post-1.0 batch 1 | pairwise E2EE, group E2EE, key transparency | 121 |
| post-1.0 batch 2 | key verification, identity/device architecture, negotiation/downgrade, transport security | 119 |
| post-1.0 batch 3 | threat model, security properties, metadata privacy | 136 |
| post-1.0 batch 4 | secret storage/hardware protection, backup recovery, attachment encryption | 112 |
| post-1.0 batch 5 | contact discovery, real-time media, profile configuration, native/web client security | 129 |
| post-1.0 batch 6 | certification lifecycle/evidence/attestations, confidence classification, advisory interoperability, vulnerability handling and disclosure | 156 |
| post-1.0 batch 7 | crypto registry, supply chain, secure development, verification, server trust, telemetry, export boundary, assurance, conformance, formal verification, integration and related specs | 156 |

**Remaining:** the rest of the 1,055 normative paragraphs, typed inter-requirement dependencies, and independently authenticated review records.
