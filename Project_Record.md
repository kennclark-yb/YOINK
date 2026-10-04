# YOINK — Project Record

> Authoritative living project record for YOINK.
>
> Sections 1–13 represent current project truth.
> Sections 14–15 preserve historical decisions and phase history.
>
> Update this record whenever project state materially changes.
>
> Last reconstructed from verified project history: 2026-10-03

---

# 0. AI Maintenance Rules

## Roles

- **ChatGPT** = TPM / technical lead / reviewer.
- **User** = operator / decision participant.
- **Codex** = repository-side execution agent.
- **Subagents** = bounded workers under a parent Codex agent when decomposition is justified.

## Project Record Authority

`Project_Record.md` is the authoritative living project record.

Before substantial work:

1. Read current `Project_Record.md`.
2. Reconcile it with verified local Git/repository state when available.
3. Treat current verified sections as authoritative.
4. Treat historical/superseded sections as context only.
5. Do not silently resolve contradictions. Flag them first.
6. Do not reopen completed, rejected, deferred, or superseded work without new evidence.
7. Preserve intentional behavior and previous rejected approaches.
8. Distinguish **IMPLEMENTED** from **VERIFIED**.
9. Keep confirmed current issues separate from theoretical risks or future improvements.
10. Follow current `RESUME HERE` unless newer verified evidence changes correct next step.

## Source Priority

Use this priority when sources conflict:

1. Verified local Git/repository state.
2. Current authoritative sections of `Project_Record.md`.
3. Verified tests, artifacts, runtime evidence, hashes, and provenance.
4. Current-session facts not yet written into record.
5. Historical/superseded material for context only.

Never silently prefer an older handoff, Codex summary, assumption, or memory over newer repository evidence.

## Status Vocabulary

Use these statuses deliberately:

- **PLANNED** — agreed work not yet started.
- **IN PROGRESS** — currently being worked.
- **IMPLEMENTED** — code/change exists but may not yet be tested.
- **VERIFIED** — supported by direct test, runtime, artifact, Git, or other suitable evidence.
- **DEFERRED** — intentionally postponed.
- **REJECTED** — considered and intentionally not pursued.
- **LOCKED** — intentional behavior or decision that should not change without explicit new evidence/decision.
- **SUPERSEDED** — historical state replaced by newer authoritative state.

Do not treat IMPLEMENTED as VERIFIED.

## Collaboration Model

ChatGPT drives:

- sequencing,
- technical recommendations,
- evidence interpretation,
- architecture decisions,
- project direction,
- Codex task definition,
- review of Codex output.

User participates in decisions and performs operator/manual QA when appropriate.

Casual user questions, frustrations, preferences, or exploratory comments do **not** automatically change project direction. Project direction changes require evidence or an explicit decision.

## Delegation Rules

Manual-first delegation.

Keep work with ChatGPT/user when it is:

- simple,
- bounded,
- inspectable,
- judgment-heavy,
- architectural,
- policy-oriented,
- primarily reasoning rather than repository execution.

Use Codex when work materially benefits from:

- repository traversal,
- broad inspection,
- repetitive inspection,
- mechanical edits,
- testing,
- execution,
- artifact verification,
- Git inspection,
- multi-file evidence gathering.

Do not delegate merely because code is involved.

Use cheapest reliable model and reasoning effort.

Prefer one Codex agent for simple linear tasks.

Use subagents only when decomposition genuinely improves execution.

No overlapping Codex tasks unless explicitly coordinated.

Do not invent work merely to keep Codex busy.

## Standard Codex Workflow

1. ChatGPT defines one bounded task.
2. Codex executes.
3. User returns Codex output.
4. ChatGPT audits Codex result against evidence.
5. Only then choose next task.

Do not chain speculative Codex tasks ahead of audit.

## Subagent Rules

When subagents are used:

- parent agent owns decomposition,
- child scopes must not overlap unnecessarily,
- parent synthesizes results,
- parent remains responsible for final correctness,
- important subagent claims must be independently checked against repository evidence.

Never accept subagent summaries blindly.

## Audit Standard

When reviewing Codex work, inspect relevant evidence such as:

- source files,
- scripts,
- tests,
- generated artifacts,
- Git status,
- diffs,
- hashes,
- provenance,
- benchmark/result rows,
- runtime behavior.

Clearly distinguish:

- **verified evidence**,
- **Codex claims**,
- **assumptions/inference**.

## Repository Safety

Preserve unrelated dirty or untracked work.

Never reset, clean, restore, stage, commit, delete, or rewrite unrelated paths.

Do not modify unrelated files while performing a focused task.

Do not rewrite Git history casually.

Use Git as recovery rather than creating permanent `_old`, `_backup`, `_verify`, or similar clutter.

Never manually delete objects from `.git/`.

## Change Philosophy

Default maintenance process:

1. Reproduce.
2. Identify narrow failing component.
3. Preserve known-good behavior.
4. Make smallest justified change.
5. User/manual QA where appropriate.
6. Verify evidence.
7. Commit only after change is proven.
8. Do not combine unrelated fixes.

Do not refactor working code merely because another architecture appears cleaner.

Do not treat theoretical concerns as production emergencies.

Do not choose implementation or policy before evidence justifies it.

## Record Maintenance

Update `Project_Record.md` whenever project state materially changes, including:

- completed work,
- verified work,
- architecture changes,
- behavior changes,
- locked decisions,
- corrected findings,
- newly confirmed issues,
- rejected approaches,
- superseded approaches,
- changed immediate next steps,
- relevant Git/checkpoint changes.

Do not rewrite history.

Preserve important prior decisions in sections 14–15 with appropriate statuses.

Keep `RESUME HERE` current.

---

# 1. Project Snapshot

**Project:** YOINK

**Original development name:** ExtractAIResponse

**Product meaning:** “Your Oversized Interactions, Nicely Kept.”

**Platform:** Windows desktop application

**Primary stack:**

- Python
- PySide6
- Playwright
- bundled Chromium headless shell

**Purpose:**

Extract public ChatGPT shared conversations into practical reusable Markdown/text so very large conversations can be preserved, split, copied, or carried into another AI session without manually copying the entire thread.

**Current release:** v1.0.0

**Current project state:** **VERIFIED — RELEASED / STABLE / DONE**

**Repository:**

`https://github.com/kennclark-yb/YOINK`

**Public release:**

`https://github.com/kennclark-yb/YOINK/releases/tag/v1.0.0`

**Primary branch:** `main`

**Canonical local repository location:**

`C:\Users\User\Desktop\Projects\YOINK`

**Status:** **VERIFIED**

YOINK is a released product, not a prototype or greenfield project.

Default posture is maintenance, not feature development.

---

# 2. Current Position

## Current State

**VERIFIED**

YOINK v1.0.0 has been publicly released and its primary behavior has been tested successfully.

The project is considered complete and stable unless deliberately reopened for:

- confirmed bugfix,
- compatibility maintenance,
- packaging maintenance,
- small justified UX improvement,
- maintenance release.

Broad feature development is not currently active.

## Current Maintenance Position

One specific share previously used as an extreme-thread stress case is unavailable in ChatGPT's own share page. User-account diagnostics established explicit upstream share errors instead of conversation data. ChatGPT's own UI could not load it.

YOINK is already known to handle very large conversations. A separate approximately 700k–800k-character thread failed once and then succeeded on retry. The unavailable share is not evidence of a YOINK scalability defect, and no confirmed active giant-thread scalability issue exists.

Broken/unavailable-share handling is **VERIFIED COMPLETE**.

---

# 3. Goals & Scope

## Current Goal

**LOCKED**

Preserve YOINK v1.0.0 as a stable working application while allowing narrow evidence-driven maintenance when justified.

## Product Scope

YOINK supports:

- public ChatGPT share links,
- full conversation extraction,
- Assistant/User/Both filtering,
- Markdown-oriented output,
- preview,
- copy workflow,
- Messages per Part splitting,
- Scratchpad,
- reset / Extract Another Thread workflow,
- preload behavior,
- update checking,
- packaged Windows operation.

## Maintenance Scope

Future work should remain narrow unless new evidence demonstrates need for broader change.

Valid maintenance categories include:

- confirmed extraction bugs,
- edge-case compatibility,
- upstream ChatGPT page/state changes,
- Playwright/browser compatibility,
- packaging maintenance,
- updater maintenance,
- small UX corrections.

## Out of Scope by Default

Unless explicitly reopened with evidence:

- major redesign,
- scraper replacement,
- broad architecture rewrite,
- speculative optimization,
- monetization,
- large new feature development.

---

# 4. Current Architecture

## Desktop Layer

**VERIFIED**

YOINK uses PySide6 for Windows desktop UI.

The application includes dynamic top-level window geometry/resizing behavior using Qt animation rather than abrupt resizing.

Known relevant Qt mechanism:

`QPropertyAnimation(self, b"geometry")`

Exact current source location must be verified from repository before editing.

## Extraction Layer

**VERIFIED**

YOINK uses Playwright to load public ChatGPT share pages.

Extraction reads ChatGPT React Router/page state rather than depending only on currently rendered DOM content.

This is important for large conversations because all messages may not be rendered simultaneously.

## Extraction Contract

**LOCKED**

YOINK extracts the **full conversation first**.

Filtering and output modes are applied **after extraction**.

Conceptual flow:

Share URL  
→ Playwright / Chromium  
→ ChatGPT page state  
→ full conversation extraction  
→ message normalization  
→ mode/filter selection  
→ preview / formatting / splitting  
→ copy/export workflow

Do not convert this into partial extraction as an optimization without specific evidence and regression testing.

## Browser Packaging

**VERIFIED**

Released package contains the Chromium headless shell required by Playwright.

Known-good packaged path:

`chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe`

Development extraction may use a user-level Playwright browser cache.

Packaged/local-browser validation can explicitly use YOINK's bundled browser.

Do not blindly delete user-level Playwright browser caches because other projects may depend on them.

---

# 5. File / Component Map

Exact current source filenames were not preserved in the prior handoff and must be verified from repository before source edits.

Do not invent paths.

Known components:

## Extraction Component

Responsibilities:

- load public ChatGPT share URL,
- wait for usable page/application state,
- retrieve React Router/page state,
- traverse conversation,
- normalize messages,
- return full extracted conversation.

## Main PySide6 UI / Controller

Responsibilities include:

- extraction workflow,
- mode/filter handling,
- preview,
- copy,
- splitting,
- Scratchpad,
- reset / Extract Another Thread,
- preload coordination,
- geometry transitions,
- error presentation.

Exact source path: **UNVERIFIED — inspect repository before editing.**

## Preload / Threading Logic

Known functional area involved in preload behavior.

Exact implementation/path: **UNVERIFIED — inspect repository before editing.**

## Packaging / Browser Discovery

Responsibilities:

- packaged browser discovery,
- bundled headless-shell use,
- packaged executable behavior.

Exact implementation/path: **UNVERIFIED — inspect repository before editing.**

## Update Checker

Known user-facing shortcut:

`Ctrl+U`

v1.0.0 update checking was verified against GitHub during release testing.

Exact source path: **UNVERIFIED — inspect repository before editing.**

## Packaged Executable

Known verified release-build path during final packaging:

`dist/YOINK/YOINK.exe`

This path reflects verified release-era local state and must not be assumed present in every future working tree.

---

# 6. Current Behavior & UX Contract

## Extraction

**LOCKED / VERIFIED**

- User provides public ChatGPT share URL.
- YOINK loads share page using Playwright.
- Full conversation is extracted.
- Filters/output modes operate on extracted conversation afterward.

## Supported Output Filtering

**VERIFIED**

Known modes include:

- Assistant
- User
- Both

Filtering must not alter underlying extraction completeness.

## Output / Workflow Features

**VERIFIED**

Current released behavior includes:

- Markdown-oriented output,
- preview,
- copy workflow,
- Messages per Part splitting,
- Scratchpad,
- reset / Extract Another Thread,
- preload behavior,
- update checker.

## Ordinary Large Threads

**VERIFIED**

Ordinary large ChatGPT shared conversations work.

Do not characterize YOINK as generally unable to handle large threads based on one maximum-length failure.

## Reset / Re-extraction

Released product supports reset / “Extract Another Thread” workflow.

Preserve this behavior when changing extraction/preload state.

## Window Behavior

Released UI uses smooth window resize/geometry transitions rather than abrupt snapping.

Treat this as intentional UX behavior.

## Upstream Broken/Unavailable-Share Error

**VERIFIED COMPLETE — automated tests and manual development-GUI verification**

If all three attempts reach explicit `serverResponse.type="error"` with an error payload instead of data, show:

> ChatGPT says nope. This share link's busted.

Three attempts and both 10,000 ms timeouts are preserved. Data still returns normally. Generic navigation/readiness failures, including mixed error/timeout attempts, retain the existing generic load-failure message.

---

# 7. Locked Decisions

## Full Extraction Before Filtering

**LOCKED**

Extract complete conversation first.

Apply Assistant/User/Both filtering afterward.

Do not optimize this into selective extraction without explicit justification.

## React State Over Naive DOM Scraping

**LOCKED**

Current extractor uses ChatGPT page/application state.

Do not replace it with naive rendered-DOM-only scraping without evidence that architecture must change.

## Preserve Known-Good Behavior

**LOCKED**

Maintenance changes must protect:

- full-conversation extraction,
- post-extraction filtering,
- preview,
- copy,
- Messages per Part,
- Scratchpad,
- reset / Extract Another Thread,
- packaged browser discovery,
- bundled headless shell,
- update checker,
- ordinary large-thread extraction.

## Minimal Maintenance Changes

**LOCKED**

Prefer surgical fixes over broad refactors.

Do not combine unrelated fixes.

## Public Release History

**LOCKED**

Do not move or rewrite public `v1.0.0` release/tag.

## Safety Tag

A local safety tag named:

`ZZ`

exists at historical baseline:

`175b03b`

**LOCKED**

Do not move or delete `ZZ` without explicit user approval.

## Git Recovery

**LOCKED**

Use Git for recovery.

Do not accumulate permanent backup copies of source files.

## Chromium Cleanup

**LOCKED**

Do not remove bundled browser assets merely because another browser exists locally.

Packaged extraction must be verified before browser packaging changes.

Do not blindly delete shared user-level Playwright caches.

## Current Product Direction

**LOCKED**

YOINK is a finished released application.

Do not reopen broad development merely because future sessions have available coding capacity.

---

# 8. Verified Baseline

## Public Release

**VERIFIED**

YOINK v1.0.0 is publicly released.

Known public release commit:

`7545aba` — `Reduce bundled Chromium footprint`

Known release history:

- `6c4f463` — Initial public release of YOINK v1.0.0
- `1c632ab` — Add v1.0.0 UI features and release polish
- `7545aba` — Reduce bundled Chromium footprint

Historical full HEAD recorded after release cleanup:

`7545aba7c5000d1f7826dc972aaa74a603415772`

Future sessions must verify current repository state before assuming local HEAD still matches this value.

## Relocation and Development Environment Recovery

**VERIFIED COMPLETE**

Canonical repository location:
`C:\Users\User\Desktop\Projects\YOINK`

Relocation preserved:

- Branch `main`, HEAD `7545aba7c5000d1f7826dc972aaa74a603415772`, and origin `https://github.com/kennclark-yb/YOINK.git`.
- Local branches and release/safety tags.
- Packaged `dist/YOINK/YOINK.exe` and packaged Chromium headless shell.

Pre/post relocation hashes matched for Project Record, packaged `YOINK.exe`, and packaged Chromium headless-shell executable.

Development environment:

**VERIFIED**

Fresh `.venv` was recreated after relocation because old generated venv launcher/activation metadata retained absolute references to the previous repository path.

- Python `3.13.15`; dependencies installed from `requirements-build.txt`.
- Playwright `1.63.0`; PySide6 `6.11.2`; Markdown `3.10.3`; PyInstaller `6.22.0`.
- Package-local Chromium headless shell installed using documented `PLAYWRIGHT_BROWSERS_PATH=0` and `playwright install chromium --only-shell`.
- Headless-shell SHA-256: `ADDFA79ABB060E1E514E155ED745D4BF96140BCA402735958BB4E223AEA0B98C`.
- Direct venv Python/pip execution works; CMD activation resolves to the new repository `.venv`.

GUI smoke: **VERIFIED**. Development GUI launched from the relocated fresh venv and remained running through approximately the 5-second smoke window.

## Regression Suite

**VERIFIED at release/cleanup baseline**

Reported result:

- 44 passed
- 2 skipped

Relocation regression verification: **VERIFIED**

Command:

`.venv\Scripts\python.exe -B -m unittest discover -s tests -p "test_*.py" -v`

Result:

- 46 run
- 44 passed
- 2 skipped
- 0 failures
- 0 errors

Skipped categories: opt-in live-share test and frozen-build assertion.

This matches the historical `44 passed / 2 skipped` baseline.

Latest upstream-share-error handling regression verification (2026-10-04): **VERIFIED**.

The same official command ran 53 tests: 51 passed, 2 skipped, 0 failures, 0 errors. The 7 added tests in `tests/test_share_loading.py` passed using synthetic React Router share state in local Chromium without public network access. Existing skips remain the opt-in live-share test and frozen-build assertion. Manual development-GUI verification: **VERIFIED COMPLETE**. Using the known broken share, YOINK displayed the exact approved wording "ChatGPT says nope. This share link's busted." The message fits the UI and RETRY remains present.

## Real Share Extraction

**VERIFIED**

Packaged application successfully extracted a real ChatGPT shared conversation.

One development extraction produced:

- 16 messages
- 13,666 characters of assistant Markdown

Package-local extraction also returned:

- 16 messages

## Packaged Executable

**VERIFIED at release baseline**

`dist/YOINK/YOINK.exe`

remained operational after Chromium cleanup.

## Browser Packaging

**VERIFIED**

Redundant full Chromium copy was removed only after live extraction testing showed bundled headless shell remained sufficient.

## Update Checker

**VERIFIED**

`Ctrl+U` correctly reported v1.0.0 as current against GitHub during release verification.

## Working Tree After Final Cleanup

**VERIFIED at historical cleanup point**

Working tree was clean.

Cleanup itself required no source commit because tracked source did not change.

---

# 9. Active Phase

## Phase

**VERIFIED — MAINTENANCE / IDLE**

v1.0.0 is released and stable.

Repository relocation and development-environment recovery status: **VERIFIED COMPLETE**.

Upstream broken/unavailable-share handling is **VERIFIED COMPLETE**, including manual development-GUI verification of the exact approved wording and confirmation that it fits while RETRY remains present. No active implementation task exists. No confirmed active giant-thread scalability issue exists; that investigation is closed unless new evidence appears.

---

# 10. Immediate Next Steps

1. Begin substantive work only for a new confirmed bug, a compatibility issue, or an explicit user-requested maintenance task.

---

# 11. Known Issues

## Broken/Unavailable ChatGPT Share

**VERIFIED COMPLETE — handling and manual development-GUI verification**

Stress-test share URL:

`https://chatgpt.com/share/6ab67761-6bb8-83ec-8cc0-3eba1087dc80`

User-account manual runtime evidence supplied for the 2026-10-04 implementation:

- HTTP navigation succeeds with status 200.
- React Router state appears within approximately 5 seconds; the expected `routes/share.$shareId.($action)` route and `serverResponse` exist.
- ChatGPT returns `serverResponse.type="error"` and `serverResponse.error="Can't load shared conversation ..."` instead of `.data`.
- The same error state remained unchanged through 60 seconds.
- ChatGPT's own browser UI shows "Could not load this ChatGPT conversation" and "Try again".

This specific failure is upstream share unavailability; the 10-second timeout is not its cause. This link is not valid evidence that YOINK cannot scale to maximum-length conversations. Ordinary large-thread behavior is not reclassified.

Implemented in `extract.py::load_share_page`: wait for data or explicit upstream error; return data normally; retry failed pages up to three attempts. Only three explicit upstream-error attempts receive:

> ChatGPT says nope. This share link's busted.

Other failures, including mixed upstream-error/timeout attempts, retain "ChatGPT page failed to load after 3 attempts." Both 10,000 ms timeouts are unchanged. Full extraction before filtering and React/page-state extraction are unchanged.

Parent automated verification: 7 focused tests passed; official full suite 53 run / 51 passed / 2 skipped / 0 failures / 0 errors. Manual development-GUI verification: **VERIFIED COMPLETE**. Against the known broken share, YOINK displayed exactly:

> ChatGPT says nope. This share link's busted.

The message fits the UI and RETRY remains present.

No confirmed active giant-thread scalability issue exists. The unavailable share was an upstream failure and is not evidence that YOINK cannot handle very large conversations.

---

# 12. Deferred / Future Considerations

## Maximum-Length Thread Diagnosis

**CLOSED / NOT ACTIVE — reopen only if new evidence appears**

YOINK is known to handle very large conversations. A separate approximately 700k–800k-character thread failed once and then succeeded on retry. The specific stress-test share documented in section 11 was an upstream broken/unavailable ChatGPT share, not evidence of a YOINK scalability defect. No confirmed active giant-thread scalability issue exists.

## Oversized-Thread Friendly UX

**DEFERRED**

Add first-failure message:

> Woah. That's a big chonker. Try it again.

Second-failure wording remains undecided.

## Historical Preload Diagnostic

**DEFERRED / NOT CONFIRMED AS PRODUCTION BUG**

A later GUI test successfully completed extraction, preview, and copy, then failed during a second preload after reset because `_preloaded_extraction` was `None`.

No established user-facing regression was confirmed.

Do not promote this to Known Issues without reproduction showing current production impact.

## README Cleanup

**DEFERRED**

An older README sentence reportedly still described Chromium size optimization as future work even though that optimization had already been completed.

Too minor to reopen v1.0.0.

Correct opportunistically if documentation is intentionally edited later.

## Donations / Monetization

**DEFERRED**

Donations were considered before v1.0.0 and intentionally omitted.

Do not add monetization unless user explicitly revisits it.

---

# 13. Overall Roadmap

## Current Direction

YOINK's intended project direction is maintenance of released v1.0.0 behavior.

### Stage 1 — Stable v1.0.0

**VERIFIED / COMPLETE**

- public release,
- packaged Windows application,
- real-share extraction,
- browser packaging,
- regression testing,
- update checking,
- release cleanup.

### Stage 2 — Evidence-Driven Maintenance

**CURRENT / ON DEMAND**

Only perform maintenance when supported by:

- confirmed bug,
- upstream compatibility change,
- packaging requirement,
- justified UX correction,
- other concrete evidence.

Workflow:

reproduce  
→ isolate  
→ smallest fix  
→ verify  
→ user QA where appropriate  
→ commit  
→ update Project Record

### Stage 3 — Maintenance Release

**PLANNED ONLY IF REQUIRED**

If a verified production fix warrants publication, create a new maintenance release such as:

`v1.0.1`

Do not rewrite `v1.0.0`.

No maintenance release is currently scheduled.

---

# 14. Decision Log

Historical record. Newer authoritative sections above take precedence.

## D-001 — Full Conversation Extraction Before Filtering

**LOCKED**

Decision:

Extract entire conversation first, then apply output filtering/modes.

Reason:

Maintains consistent source conversation and avoids partial extraction behavior.

Status remains current.

---

## D-002 — React/Page-State Extraction

**LOCKED**

Decision:

Use ChatGPT React Router/page state rather than relying solely on rendered DOM.

Reason:

Large conversations may not have all messages rendered simultaneously.

Status remains current.

---

## D-003 — PySide6 Desktop Application

**IMPLEMENTED / VERIFIED**

Decision:

YOINK ships as Windows desktop application using PySide6.

Status remains current.

---

## D-004 — Playwright Browser Loading

**IMPLEMENTED / VERIFIED**

Decision:

Use Playwright to load public ChatGPT share pages.

Status remains current.

---

## D-005 — Bundled Chromium Headless Shell

**IMPLEMENTED / VERIFIED**

Decision:

Package required Chromium headless shell with YOINK.

Later optimization removed redundant full Chromium copy after live validation.

Status remains current.

---

## D-006 — Do Not Delete Shared Browser Cache Blindly

**LOCKED**

Decision:

User-level Playwright cache may serve other projects.

Do not remove it as part of YOINK cleanup without specific justification.

---

## D-007 — Small Focused Git Workflow

**LOCKED**

Preferred sequence:

known-good state  
→ focused change  
→ user test / verification  
→ commit

Avoid unrelated edits and backup-file clutter.

---

## D-008 — Public v1.0.0 History Is Immutable

**LOCKED**

Do not move public release tag or rewrite existing release history.

Future fixes use new maintenance release.

---

## D-009 — Preserve `ZZ` Safety Tag

**LOCKED**

Historical tag:

`ZZ` → `175b03b`

Do not move/delete without explicit approval.

---

## D-010 — Maximum-Length Thread Is Not General Large-Thread Failure

**LOCKED pending contrary evidence**

Observed ordinary large threads work.

One maximum-length conversation fails.

Do not generalize one extreme failure into claim that large-thread support is broken.

---

## D-011 — Maximum-Length Investigation Deferred

**DEFERRED**

User explicitly chose to put issue on hold.

Do not consume development effort on it until reopened.

---

## D-012 — Oversized Thread First-Failure Copy

**PLANNED / DEFERRED**

Desired wording:

> Woah. That's a big chonker. Try it again.

Second-failure wording remains unlocked.

---

## D-013 — No Broad Refactor Without Evidence

**LOCKED**

Do not replace working architecture merely for elegance.

Reproduce and isolate first.

---

## D-014 — Donations Not Included in v1.0.0

**DEFERRED**

Monetization was considered and intentionally omitted.

---

# 15. Phase History

Historical record. Do not treat superseded state as current project state.

## Phase — ExtractAIResponse Development

**SUPERSEDED**

Project originally developed under name:

`ExtractAIResponse`

Core extraction concept, UI, Playwright integration, filtering, and workflow evolved during this phase.

Superseded by released YOINK branding/product state.

---

## Phase — YOINK Productization

**COMPLETE**

Project renamed/released as:

**YOINK — Your Oversized Interactions, Nicely Kept**

Work included release-ready UI behavior, packaging, update checking, browser bundling, and distribution preparation.

---

## Phase — v1.0.0 Public Release

**VERIFIED / COMPLETE**

Public repository and release created.

Release archive:

`YOINK-v1.0.0-windows-x64.zip`

Historical archive size was approximately 201 MB.

Release artifact remains preserved by GitHub release.

---

## Phase — Chromium Footprint Reduction

**VERIFIED / COMPLETE**

Redundant packaged Chromium content was reduced.

Known public release HEAD became:

`7545aba Reduce bundled Chromium footprint`

Bundled headless shell remained operational after cleanup.

---

## Phase — Post-Release Cleanup

**VERIFIED / COMPLETE**

Historical cleanup removed local generated/redundant items including:

- `build/`
- local `YOINK-v1.0.0-windows-x64.zip`
- `dist/YOINK-QA/`
- redundant full Chromium copy inside project environment

Approximately 1.64 GiB was recovered.

`.git/` was deliberately left untouched.

Tracked source did not change.

---

## Phase — Maximum-Length Thread Stress Test

**DEFERRED**

A ChatGPT conversation that had itself reached platform maximum conversation length failed extraction.

Ordinary large conversations remained functional.

Investigation was intentionally paused.

No production patch was made.

---

## Phase — Repository Relocation and Development-Environment Recovery

**VERIFIED COMPLETE**

The old `ExtractAIResponse` source directory was empty after relocation and was subsequently manually deleted by the user.

---

## Phase — Current Maintenance State

**CURRENT**

YOINK remains:

- released,
- stable,
- v1.0.0,
- done by default,
- available for evidence-driven maintenance only.

---

# RESUME HERE

YOINK repository relocation and development-environment recovery are **VERIFIED complete**.

Canonical local repository:
`C:\Users\User\Desktop\Projects\YOINK`

YOINK is in **MAINTENANCE / IDLE** with no active implementation task. Broken/unavailable-share handling is **VERIFIED COMPLETE**. Manual development-GUI verification displayed exactly "ChatGPT says nope. This share link's busted."; it fits the UI and RETRY remains present.

Begin new substantive work only for a new confirmed bug, a compatibility issue, or an explicit user-requested maintenance task. The giant-thread investigation is **CLOSED / NOT ACTIVE** unless new evidence appears. The optional "big chonker" UX remains deferred under section 12.
