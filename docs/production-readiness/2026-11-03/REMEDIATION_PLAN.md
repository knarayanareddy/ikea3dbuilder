# ikea3dbuilder remediation plan

All tasks are planned, not executed. Owner approval is required before changing access, externally hosting assets, or representing a simulation as assembly guidance.

## Phases and dependencies

| Phase | Entry | Exit |
|---|---|---|
| Baseline | Pinned source and isolated fixture data | IB-T1 records reachable behavior and backups |
| Confirmed defects | IB-T1 | IB-T2 rejects untrusted writes and traversal |
| Risk-based security and automation | IB-T2 | IB-T3 tests malformed input and supply chain |
| Domain and UX | IB-T1 | IB-T4 reviews representative builds and accessible use |
| Release and independent acceptance | IB-T3 and IB-T4 | IB-T5 demonstrates recovery and approved deployment |

## Task dependency map

| Task | Depends on | Blocks | Why |
|---|---|---|---|
| IB-T1 | none | IB-T2, IB-T4 | Establishes safe reproduction fixtures, baseline behavior, and backup evidence. |
| IB-T2 | IB-T1 | IB-T3 | Fixes the confirmed write/traversal/path-disclosure defects before hardening tests are meaningful. |
| IB-T3 | IB-T2 | IB-T5 | Adds negative security tests, dependency provenance, and proposed automation gates for the constrained server/tooling model. |
| IB-T4 | IB-T1 | IB-T5 | Separates unverified prototype fidelity/accessibility claims from anything that might be released as guidance. |
| IB-T5 | IB-T3, IB-T4 | release decision | Requires both technical controls and owner/domain validation before release, rollback, and recovery evidence can count. |

### IB-T1 — Reproduce safely (IB-1–IB-5)
Prerequisite: disposable checkout and synthetic product files; observed `tools/server.py`.
1. Record interpreter and platform, and back up the fixture product directory.
2. In an isolated network namespace, demonstrate save, catalogue and page lookup with allowed inputs.
3. Test unauthorized save and a traversal fixture without touching real user files; capture responses without local paths.
Deliverable: reproducible baseline and failure cases. Verification: independent reviewer repeats it from the pinned revision.
- [ ] Baseline demonstrates only synthetic-data effects.
- [ ] Exposure, response and recovery evidence are recorded.

### IB-T2 — Constrain authoring and lookup (IB-1, IB-2, IB-5)
Prerequisite: IB-T1 and owner decision on authorized writers; observed `tools/server.py`.
1. Bind to loopback by default and require explicit opt-in plus appropriate authentication and authorization for remote writes.
2. Validate one product slug; resolve and verify paths remain under the product root, including symlink cases, for reads and writes.
3. Remove root-path disclosure and implement conflict-safe atomic writes to avoid overwriting concurrent edits.
Deliverable: constrained server and documented local workflow. Verification: attempt unauthorized POST, encoded traversal, absolute path, symlink escape and concurrent writes against a running test server; each must reject or preserve both intended updates.
- [ ] No unauthorized write or out-of-root read succeeds.
- [ ] Legitimate authoring still saves and reloads the intended product.

### IB-T3 — Input, dependency and automation gates (IB-3; preventive)
Prerequisite: IB-T2; observed `tools/server.py`, `tools/test_chrome.py`, `lib/`.
1. Limit request sizes and validate content type, JSON shape, Origin and Host for the approved access model.
2. Inventory vendored Three.js/browser assets separately from auxiliary tooling dependencies such as the `websockets`-based Chrome smoke script, and record provenance plus an update policy for each surface.
3. Define a proposed test command and CI workflow for handler integration and browser smoke tests; no existing script is presumed.
Deliverable: repeatable server and browser regression suite. Verification: submit oversized, malformed and cross-origin requests, and deliberately remove a rejection to ensure its test fails.
- [ ] Security negatives fail on deliberately broken protection.
- [ ] Dependency versions and provenance are recorded without secrets.

### IB-T4 — Assembly fidelity and accessible interaction (IB-4)
Prerequisite: product owner and permission to use manuals; observed `README.md`, product inventory, viewer.
1. Select representative products and independently compare every displayed step, part and warning to the authorized manual and physical example.
2. Label incomplete, approximate or unreviewed content and provide a clear link to authoritative instructions.
3. Test keyboard control, text alternatives, reduced motion and loading/error states with actual users and assistive technology.
Deliverable: per-product validation matrix and accessible fallback. Verification: independently reproduce one incorrect-step fixture and ensure it is flagged, not presented as validated.
- [ ] Domain reviewer signs off each claimed validated product.
- [ ] Accessible fallback works without 3D or motion.

### IB-T5 — Release and recovery (preventive)
Prerequisites: IB-T3 and IB-T4; observed product data and server.
1. Agree storage ownership, licensing, access and release targets.
2. Back up synthetic and then approved production data, restore it to an isolated environment, and verify product JSON and assets.
3. Independently exercise the release and a rollback to the last known-good artifact and data snapshot.
Deliverable: release and recovery record. Verification: inspect restored product and manual references in a clean browser.
- [ ] Restore and rollback are observed, not inferred from a backup file.
- [ ] Owner approves deployment and rights; independent reviewer signs off.

## Owner approval gates

- [ ] Owner classifies the server as local-only authoring or approves a specific remote-write model with named authorized users.
- [ ] Owner approves what request logging is retained, where it is stored, and when it is deleted.
- [ ] Owner confirms rights for manuals, screenshots, product imagery, and any claimed assembly-guidance use.
- [ ] Owner approves separate maintenance policy for vendored viewer assets and auxiliary tooling dependencies.

## Release policy and acceptance checklist

- [ ] Release only the approved artifact/data pair that passed IB-T3 and IB-T4 verification at the same revision.
- [ ] Security tests, dependency review, product validation and accessibility results are attached to the proposed release.
- [ ] Release notes distinguish validated products from illustrative prototypes and do not claim mechanical/safety certification.
- [ ] The approved deployment target, access model, storage owner, and restore owner are named.
- [ ] A clean build artifact and matching approved data snapshot are identified as the release pair.

## Rollback policy

- [ ] Stop write traffic before replacing artifacts or product JSON.
- [ ] Restore the last verified artifact together with its matching verified data snapshot, not a mixed pair.
- [ ] Re-run the agreed smoke and negative checks after rollback before reopening access.
- [ ] Record who initiated rollback, why, and what evidence confirmed the restored state.

## Recovery drill checklist

- [ ] Restore backed-up product JSON and referenced assets into an isolated environment first.
- [ ] Verify at least one representative kit loads the expected manual references and product metadata from the restored snapshot.
- [ ] Confirm unauthorized write attempts still fail after restore.
- [ ] Promote the recovery procedure to the release environment only after owner review of the isolated drill output.

## Definition of done for acceptance

- [ ] Retention, credentials, monitoring and backups have named owners.
- [ ] Release, rollback, and recovery evidence are observed and attached, not inferred from config or backup presence.
- [ ] No assembly certification is implied, and prototype/runtime/rendering/geometry limits remain stated in release-facing docs.
