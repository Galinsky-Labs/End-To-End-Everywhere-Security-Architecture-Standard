# AUD-19.1 — Group input parser crash containment

This slice prevents Python unhashable JSON structures (nested dictionaries, arrays, or null values) from crashing E2EESA's group policy/evidence reference validator. Malformed profile, protocol, cipher suite and membership authorization fields now return deterministic validation errors instead of triggering unhandled set/dict-key operations. Semantic validation still rejects malformed member identifiers; the engine must not silently drop them as an accepted membership.

**Reference scope only.** This addresses one narrow input boundary in the standard's group reference code. It does **not** establish deployed parser isolation, memory/time/CPU bounds, safe native codecs, network ingress hardening, fuzzing of all schemas, or real-client conformance. AUD-19 remains pending until those additional requirements are measured.

## AUD-19.2 — Parser boundary evidence gate (reference)

`scripts/parser_boundary_reference.py` describes the minimum platform-specific evidence for parser process isolation: separate process, enforced OS sandbox, denied key-material and network access, validated IPC, input and resource bounds, crash containment, and artifact-bound host-boundary, fuzzing and source-build references. A separate worker name or memory-safe wrapper does not establish isolation, and a browser worker alone is not accepted as proof of OS-level process isolation.

The gate returns `boundary_supported=false` even for structurally complete evidence until full runtime verification exists. Actual native and web runtime enforcement, sandbox profiles, adversarial media fuzzing, exploit attempts against key access and egress, and independently verified captures remain outstanding.
