# End To End Everywhere Security Architecture Standard (E2EESA)

**Original 50-milestone development plan:** [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md). **Separate corrected audit remediation:** [docs/AUDIT_REMEDIATION_PLAN.md](docs/AUDIT_REMEDIATION_PLAN.md).

E2EESA is the upstream, implementation-neutral security architecture standard for End To End Everywhere technical projects.

The standard separates:

- **security invariants** that compliant implementations cannot disable;
- **versioned profiles** for areas where multiple serious architectures are defensible;
- **capabilities** that apply only to some product classes; and
- **experimental profiles** that are not production recommendations.

## Repository layout

- `spec/` — normative and informative specification material
- `schemas/` — machine-readable configuration/evidence schemas
- `registry/` — machine-readable standard terminology and future registries
- `profiles/` — versioned standard profiles
- `fixtures/` — valid and invalid conformance examples
- `adr/` — architecture decision records
- `scripts/` — repository validation tooling
- `tests/` — validation tests

## Normative foundation

E2EESA defines its requirement language in `spec/normative-language.md` and its core vocabulary in `spec/terminology.md`. Implementations and later profiles must use those definitions consistently rather than silently redefining security terms.

## Development rule

Security-sensitive changes are made through reviewed pull requests. Controversial choices are represented as explicit profiles rather than hidden implementation defaults.

## Current status

**E2EESA 1.0.0 is the owner-authorized stable engineering edition of the implementation-neutral architecture standard.** It is published from a validated, immutable rc.2 source candidate. Conformance to the standard requires independent scoped product evidence; this publication alone does not certify any product. External expert review remains pending and is not falsely reported as complete.

Audit v2 normative/reference-tooling work is recorded in registry/audit-remediation.json. Optional PQ MLS research and completion of individual requirement-level rationales are tracked separately; at the source rc.2 freeze, 21 of 1,055 paragraphs had individual analysis and no externally authenticated review. Failed security tests or demonstrable vulnerabilities remain genuine reasons to withhold affected conformance claims.

## End-to-End Everywhere progress

The canonical [security/e2eesa-status.json](security/e2eesa-status.json) records standard implementation, complete testing and independent expert review separately. Engine Room reads it automatically from GitHub. All initial stages are pending; existing profile locks and approved decisions remain authoritative. Read [adoption and independent-account instructions](docs/E2EESA_ADOPTION.md), and run `python3 scripts/validate_e2eesa_status.py`. Record validation does not establish product security or certification.
