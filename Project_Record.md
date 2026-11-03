# YOINK — Project Record

> Authoritative living project record for YOINK.
>
> Sections 1–13 represent current project truth.
> Sections 14–15 preserve historical decisions and phase history.
>
> Update this record whenever project state materially changes.
>
> Last reconstructed from verified project history: 2026-10-03
>
> Current-state reconciliation: 2026-11-03. Checkpointed Stage 1A, Option 3 styling, Stage 1B, Stage 1C and Task B production blue CRT. Retained original background; deferred cell division. Planned Stage 2 Lorekeeper with optional provider-neutral AI. v2 remains development software; v1.0.0 is the only published release.

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

## Project documentation voice

- Write README, project records, architecture, decisions, histories, changelogs, release notes, pull requests, commit subjects/bodies, and audit summaries as **developer-authored project text**, not commentary on a conversation.
- Use concise, subjectless outcomes: **“Adopted blue CRT shutdown design.” “Deferred cell division after the prototypes failed visual review.” “Designed AI integration to remain provider-neutral.”**
- Avoid “we”, “the owner”, “the user”, “Codex recommended” and other actor/agent narration in finished project prose. Neutral technical descriptions are appropriate.
- Summarize audits with **Status / Changes / Checks / Evidence / Limitations**, not actor narration. Record executor, tool/model, environment, SHA, and evidence references as separate metadata only when relevant to reproducibility; keep reported versus independently verified claims distinct.
- Preserve source identity, authorization facts, test provenance and historical audit records. Never rewrite published Git history, previous release notes or original audit ZIPs solely to change voice; use clear, impersonal future messages.

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

**Current project state:** **v1.0.0 VERIFIED RELEASED / STABLE; v2 Stage 1A, Option 3, Stage 1B, Stage 1C AND TASK B CHECKPOINTED; STAGE 2 LOREKEEPER PLANNED; DEVELOPMENT SOFTWARE**

**Repository:**

`https://github.com/kennclark-yb/YOINK`

**Public release:**

`https://github.com/kennclark-yb/YOINK/releases/tag/v1.0.0`

**Primary branch:** `main`

**Canonical local repository location:**

`C:\Users\User\Desktop\Projects\YOINK`

**Status:** **VERIFIED**

YOINK is a released product, not a prototype or greenfield project.

Maintained stable v1.0.0 separately from the v2 development program initiated on 2026-10-25. Checkpointed Stage 1A, Option 3 styling, Stage 1B, Stage 1C and Task B blue CRT shutdown. Planned Stage 2 Lorekeeper under [ROADMAP_V2.md](ROADMAP_V2.md). No v2 packaged executable or public release verified.

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

Kept broad **v1 development** closed to maintenance. Checkpointed v2 Stage 1A, Option 3, Stage 1B, Stage 1C and Task B. Planned Lorekeeper as the next stage; [ROADMAP_V2.md](ROADMAP_V2.md) governs scope and acceptance gates.

## Current Maintenance Position

One specific share previously used as an extreme-thread stress case is unavailable in ChatGPT's own share page. User-account diagnostics established explicit upstream share errors instead of conversation data. ChatGPT's own UI could not load it.

YOINK is already known to handle very large conversations. A separate approximately 700k–800k-character thread failed once and then succeeded on retry. The unavailable share is not evidence of a YOINK scalability defect, and no confirmed active giant-thread scalability issue exists.

Broken/unavailable-share handling is **VERIFIED COMPLETE**.

Separate **ChatGPT Project-shared** and **Codex snapshot** formats were investigated on 2026-10-25–26 (Phases A–A4). A Project conversation was structurally accessible in a user-authenticated browser, but full-history completeness and a safe production integration were **NOT VERIFIED**. Deferred support and closed [Issue #2](https://github.com/kennclark-yb/YOINK/issues/2) as a known limitation; closure is **not** a software fix. No v1.1.0 release is planned from that investigation.

---

# 3. Goals & Scope

## Current Goal

**LOCKED**

Preserve stable v1.0.0 while advancing the separately scoped v2 roadmap in [ROADMAP_V2.md](ROADMAP_V2.md). Checkpointed Stage 1C and Task B blue CRT shutdown; next Stage 2 Lorekeeper discovery and provider-neutral AI foundation remain planned.

## Product Scope

YOINK supports:

- **standard public ChatGPT share URLs** (`https://chatgpt.com/share/...`) only,
- full conversation extraction for that supported URL format,
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
- unapproved feature development **outside** the explicitly authorized v2 roadmap.

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

YOINK v1.0.0 is a finished released application. Preserve its verified behavior and release history. V2 feature development was subsequently and explicitly authorized on 2026-10-25, exclusively within [ROADMAP_V2.md](ROADMAP_V2.md). No speculative work outside that plan.

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

## Accepted Option 3 background — 2026-11-01

Adopted static cobalt-grain artwork with native rendering and 84% opaque inner panels. The accepted artwork and organic window silhouette are unchanged. `YOINK.spec` includes the background asset in the PyInstaller configuration. Source and focused packaging tests passed; packaged executable verification remains pending. The local Option 3 checkpoint is `f64bf97` (2026-11-01). Stage 1B subsequently checkpointed at `bca121d5eb5c1d9da22a91c985a2f6195275a70e`.

## Stage 1A — Direct-to-Scratchpad

**COMPLETED / TESTED / ACCEPTED / CHECKPOINTED** — Stage 1A UI accepted on 2026-10-31; checkpoint `e0a153c935ce7460e80eaf736a1f313ffa7013c4`.

Confirmed development-source behavior:

- Per-part arrow appends original conversation content into Scratchpad; independent per-part copy preserves the original content.
- Multi-level app-managed Undo, rapid duplicate-click suppression with deliberate repeats permitted, preserved manual notes, and transient confirmation feedback.
- Unicode-preserving Scratchpad copying, subject to the documented manual paragraph-break replacement limitation: manually replaced paragraph breaks, including those restored by editor Undo, may copy as LF. The application documents this limitation.
- Smooth Results scrolling and hover interactions; compact extraction panel and taller Results panel.
- Accepted organic outer-window silhouette, 16 px inner-panel gap, and improved expansion/reset animation.
- Slower extraction-loading phrase transitions; slimmer title bar with Maximize removed.

Accepted audit package: `C:\Users\User\Desktop\artifacts-yoink\new\YOINK_Stage-1A_Unicode-Finality_2026-10-31_190124`. The twelve implementation/test files were compared byte-for-byte with its `changed_files` snapshots before this checkpoint's documentation edit; all matched.

Historical Stage 1A verification: full offline suite **75 tests run, 73 passed, 2 expected skips**; native Windows focused tests **6 passed**; `git diff --check` passed. That Stage 1A checkpoint reran its checks; see its external audit package. Current Stage 1C validation is recorded separately below.

No new packaged executable or public release has been verified. Optional live-share and packaged-build verification remained outside that Stage 1A checkpoint. At that historical point Stage 1B had not begun; its later checkpoint is recorded below. Authorized local Stage 1A checkpoint on `feature/v2-stage1a-scratchpad`, based on `d562522b05f5e12bc19fd54482760409ab4c7855`; recorded resulting SHA externally to avoid a self-referential commit.


## Stage 1B and Stage 1C accepted baseline — 2026-11-02

**Stage 1B — LOCALLY CHECKPOINTED:** deterministic pure-Python selection core at `bca121d5eb5c1d9da22a91c985a2f6195275a70e`; source-preserving fractional/disconnected ranges and role-filtered resolution.

**Stage 1C — IMPLEMENTED / AUDITED / ACCEPTED:** connected Extract/Results/tool workspace with organic silhouettes, Parts Picker, Preview and Scratchpad navigation, state retention, source selection, copy/append/Undo, bounded geometry, hover and native dragging repair. Preserve accepted cobalt/icy-blue colors, grain, layout, spacing, 84% panel opacity and animations. Extraction remains full-source before filtering.

**Append notification — IMPLEMENTED / AUDITED / ACCEPTED:** fixed 18 px feedback slot, 220 ms entrance from +10 px through restrained -2 px overshoot to 0 px, settled updates on repeated append, existing dismissal lifecycle and 250 ms fade. Reset/shutdown cancel entrance; reduced motion stays settled. Wording, append data, duplicate feedback and Undo are preserved.

**Background — LOCKED:** original `assets/static_grain_option3.png`, byte-identical, remains the final approved production artwork. Retain the accepted native-drag changes in `gui/background.py`. Three unsuccessful isolated cell-division visual approaches were diagnostic-only and never integrated into production. **Deferred cell division on 2026-11-02 after three unsuccessful visual prototypes; not implemented or accepted.** The earlier incomplete-experiment status is superseded by this deferral, not by a successful implementation.

Prior audited delivery: `C:\Users\User\Desktop\artifacts-yoink\new\YOINK_Stage-1C_Finite-Cell-Division-Background_2026-11-02_175537`; its 76-file delivery inventory matches this checkpoint's incoming files byte-for-byte. Prior tests reported 167 run, 165 passed and two expected skips, plus five notification contracts on native Qt at 100% and 150% scale. Current checkpoint reruns and exact results are in its external validation report; no self-referential commit hash is inserted here.

**Validation limits:** v2 remains development software. No v2 packaged-EXE build/test, new live-share extraction, broad hardware/DPI qualification or new physical drag test is claimed by this checkpoint. The opt-in live-share and frozen-build assertions are expected skips. Existing Scratchpad manual paragraph-break copying limitation remains. v1.0.0 is the only verified published release.

**Sequence at the accepted Stage 1C checkpoint (historical):** separately instructed **Task B — shutdown-screen redesign**, preserving existing working shutdown until that later task; **Stage 2 — Project Library** follows Task B. No shutdown redesign, executable build, tag, merge or release is part of this baseline checkpoint.

---

## Task B first shutdown presentation — 2026-11-02 (superseded)

**HISTORICAL FIRST ITERATION.** Initially accepted separate original-GIF/quip presentation, later superseded by the production blue CRT design recorded below. The following describes that earlier iteration and its validation.

**IMPLEMENTED / LOCALLY VERIFIED — TPM INSPECTION AND OWNER VISUAL APPROVAL PENDING; NOT INTEGRATED OR RELEASED.**

The shutdown presentation now uses two independent floating elements: the unchanged original `assets/shutdown.gif`, painted at approximately 220 × 140 logical pixels with an aspect-preserving, antialiased rounded Qt clip; and the existing randomly selected quip in its own small dark rounded container, separated by a transparent 12 px gap. The enclosing dark frame is removed. QMovie is parent-owned, stopped on close and deleted with the presentation. `gui/main_window.py`, shutdown overlay, centering, idle timer and worker completion chains are unchanged.

`assets/shutdown_system_optional.gif` is a separate 480 × 306, black/blue terminal-text alternative for visual approval only. Production continues to load `shutdown.gif`. Its 50 encoded frames loop over 3000 ms; nominal 50 ms source frames merge where identical. The light-blue shimmer moves top to bottom. Authoring uses Pillow and the local Consolas Bold font; no new runtime dependency or font asset was added.

Validation: full offline suite **173 run, 171 passed, 2 expected skips**, 0 failures/errors. Six focused tests passed offscreen and on native Windows Qt at both `QT_SCALE_FACTOR=1` and `1.5`. Tests cover frame alpha/clipping, separate message container, all quips fitting, GIF identity, QMovie decode/advance/loop, idle shutdown and simultaneous active preload/extraction cleanup. Native real-main-window captures at both scales show the original GIF over the existing dimming overlay; native held-worker runs finish with no screen/overlay/worker references left. Optional GIF was separately previewed through native QMovie. Only this machine and Qt scale-factor settings were checked; live network extraction, physical display-scale changes, broad hardware qualification and packaged EXE testing are not claimed. The existing two opt-in skips remain unchanged.

Audit: `C:\Users\User\Desktop\artifacts-yoink\new\YOINK_Task-B_Shutdown_2026-11-02_201500`, including report, exact diff, native captures, asset, tools, tests, hashes and consolidated ZIP. No staging, commit, push, merge, tag, release or EXE build was performed. At that historical checkpoint, independent inspection and visual acceptance were pending. Accepted Stage 1C remained locked.

---

## Task B final production blue CRT — 2026-11-02

**HISTORICAL PRE-CHECKPOINT STATUS — IMPLEMENTED / LOCALLY VERIFIED.** Replaced the first shutdown presentation with the blue CRT; completed final visual corrections and source audit. **Not yet committed at this historical stage; subsequently checkpointed in `7de0613`. No packaged v2 EXE or release.**

The working optional renderer was moved into `gui/shutdown_crt.py`; `gui/shutdown_screen.py` supplies exactly one `random.choice(EXIT_MESSAGES)` per instance. All 22 strings and their order remain unchanged. Production never imports `tools/preview_shutdown_crt.py`; that tool now previews the same GUI component. The CRT stays 220 × 140 logical pixels, with two centered procedural block-glyph lines, SYSTEM / SHUTDOWN. Bright-blue faces, dark-blue depth, narrow bevels and restrained illumination provide the accepted retro typography without a heading-font dependency. One small, centered terminal quip remains at the bottom. The obsolete decorative status lines and separate floating capsule are removed.

The accepted raster/background/perimeter/grain/vignette are preserved. The moving scan highlight uses a three-times-broader soft Gaussian profile with unchanged peak amplitude, downward path and 50 ms cadence. The historically named `assets/shutdown_system_optional.gif` is now the intended production CRT surface: 480 × 306, 60 frames, 3000 ms infinite loop, without baked text. `assets/shutdown.gif` remains byte-identical as an inactive legacy asset. `YOINK.spec` includes the CRT surface and retains the legacy asset; only its collection recipe was tested, with no executable build.

`gui/main_window.py` is byte-identical: frameless/translucent/always-on-top presentation, integer centering, existing dimming, 1200 ms idle timing, repeated-close guard, worker completion gating and overlay cleanup are unchanged. Parent-owned QMovie stops on close and is deleted with the screen. No new runtime dependency. Accepted Stage 1C artwork, geometry, native dragging, notifications, Scratchpad, Picker and extraction are unchanged.

Final validation: **180 offline tests run, 178 passed, 2 expected skips**, zero failures/errors. **13 focused shutdown tests pass offscreen and on native Windows Qt at both 100% and 150% scale factors.** Contracts cover all 22 quips fitting, one random selection, production asset, two-line title bounds/visible faces, no obsolete status text/capsule, broadened restrained scan, playback/looping, disposal, idle timing and concurrent active preload/extraction cleanup. The two expected skips remain opt-in live-share extraction and frozen-build verification.

Native production evidence uses the real MainWindow closeEvent, with a deterministic local preload extraction hold for capture and normal completion on release. Captures at DPR 1.0/1.5 show the corrected title, normal random quips, a longest quip and three scan positions. Long-message evidence seeds only the external harness, choosing from the actual collection through the normal random call; production is unseeded. Actual-size crops are 220 × 140 / 330 × 210 physical pixels. Wider OS/hardware/monitor, physical display-scale changes, live-network extraction and packaged-EXE qualification are not claimed.

Audit: `C:\Users\User\Desktop\artifacts-yoink\new\YOINK_Task-B_Final-Production-CRT_2026-11-02_212136`, including production screenshots, reference comparison, scan strip/preview, exact incoming/final files and diffs, tests, hashes, execution summary and ZIP. No stage, commit, push, merge, tag, release or EXE build. At this historical stage, final visual review and checkpoint remained pending; later completed under Task B. Stage 2 follows.

---

# 9. Active Phase

## Phase

**v1 VERIFIED RELEASED / MAINTENANCE; v2 STAGE 1C AND TASK B CHECKPOINTED; STAGE 2 LOREKEEPER PLANNED**

v1.0.0 is released and stable.

Repository relocation and development-environment recovery status: **VERIFIED COMPLETE**.

Upstream broken/unavailable-share handling is **VERIFIED COMPLETE**, including manual development-GUI verification of the approved wording and RETRY. Investigations into Project-shared and Codex snapshot URLs are **DEFERRED / NOT IMPLEMENTED**; [Issue #2](https://github.com/kennclark-yb/YOINK/issues/2) is closed as a known limitation, not a fix. No v1.1.0 release occurred. Checkpointed Stage 1A, Option 3, Stage 1B, Stage 1C and Task B blue CRT shutdown. Stage 2 Lorekeeper remains planned. Preserved the incomplete successor TPM handoff status and closed giant-thread investigation; no confirmed active scalability defect.

---

# 10. Immediate Next Steps

1. Begin Stage 2 Lorekeeper read-only project-folder inventory and document discovery; do not start uncontrolled AI writing.
2. Preserve accepted Stage 1C artwork/workspace, Scratchpad append, and Task B CRT shutdown at published feature-branch checkpoint `7de0613309d977b3e5df0523ea05e2e882662454`.
3. Keep AI optional and provider-neutral; any Codex, Claude or local integration requires separate capability, security and consent validation.
4. Maintain zero unapproved writes, protected original checkout, deferred cell-division and share-format investigations. Keep successor TPM Task 4 incomplete until separately resolved.

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

## ChatGPT Project-shared conversation links — known limitation

**DEFERRED / ISSUE CLOSED — NOT IMPLEMENTED — NOT A VERIFIED COMPLETE EXTRACTION**

[Issue #2 — Known limitation: ChatGPT Project-shared conversation extraction](https://github.com/kennclark-yb/YOINK/issues/2) was closed on 2026-10-26 after four bounded investigations (A, A2, A3, A4). Its closure does **not** signify that support was implemented or the problem fixed.

- **Unsupported URL shape:** `https://chatgpt.com/g/<project-slug>/shared/c/<conversation-id>?owner_user_id=<user-id>`. Current GUI validation accepts standard `/share/...` URLs only.
- **A (initial probe):** two anonymous Playwright requests were HTTP 403; a confirmation identified a Cloudflare challenge. No conversation data was inspected. This finding alone did not establish a Project membership or login requirement.
- **A2 (controlled comparison):** unchanged production code extracted a standard public share with **277 messages (98 user / 179 assistant) and 704,368 characters**. Under the same browser environment, the Project link returned **307 → 403** with a Cloudflare challenge, no usable application data. Synthetic loader tests: 7 passed. The standard-share positive control excludes a universal Playwright extraction failure.
- **Signed-out browser test:** opening that Project URL in an Incognito window required ChatGPT sign-in.
- **A4 (authorized-browser probe):** after interactive sign-in, a dedicated headed browser opened the target Project conversation. A read-only inspector found **65 nodes** (5 user, 39 assistant, 20 tool and one empty root), **64 unique message IDs** matching mapping keys, and an internally consistent current ancestry across repeated observations. **37 string parts in 33 messages totaled 65,870 UTF-16 code units.** Existing v1 text-only extraction rules would retain **13 messages (5 user, 8 assistant), totaling 30,433 UTF-16 units**. The page used an **in-page query cache**, not the standard-share React Router loader.
- **Unverified:** full historical/server-side completeness, long-thread pagination/virtualization, supported/stable page-data interface, exact omission policy for code/recaps/tool/thought structures, failure handling after authorization expires, and reliable packaged integration. The A4 node graph's internal consistency is **not** proof that every historical message was loaded.

**Decision:** deferred Project-link compatibility. No GUI/extractor/credential-handling changes were approved or made, no v1.1.0 binary/tag/release was created, and no broader authentication integration is authorized. Revisit only with a privacy-preserving, user-authorized and maintainable import mechanism **plus verified source completeness and an explicit included/omitted-content contract**. Do not ship a regex-only acceptance change or claim the 13 text messages are a complete original transcript.

## Codex shared-snapshot URLs — known limitation

**DEFERRED / NOT IMPLEMENTED.** Separate snapshot URLs have the form `https://chatgpt.com/s/cx_...`, not standard ChatGPT `/share/...`. In A3, three attempts using the existing production loader and two independent Playwright probes all encountered **307 → 403 Cloudflare challenges**, without exposing snapshot data. The owner opened the example anonymously in an ordinary browser but observed only what appeared to be a limited slice of the original session. **Unknown:** underlying snapshot completeness, page-data schema, and whether all original Codex events are included. Do not label this as an authenticated-only URL, a YOINK extractor bug, or a verified complete Codex export.

**Evidence/provenance:** Phases A–A4 used independent diagnostic scripts, synthetic verification, source inspections and run-specific audit packages under `C:\\Users\\User\\Desktop\\artifacts-yoink\\new`. The previous Codex task branch was `fix/project-shared-links-v1.1.0` at local HEAD `fb395b9`; all 28 final diagnostic files were untracked, and no production edits or Git publication occurred. Audit findings describe bounded experiments, not released capabilities.

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

Maintained distinct tracks: **stable v1.0.0 maintenance** and **v2 development**. Checkpointed Stage 1C and Task B blue CRT; planned Stage 2 Lorekeeper under [ROADMAP_V2.md](ROADMAP_V2.md).

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

No maintenance release is currently scheduled. In particular, the hypothetical `v1.1.0` new-share-format release was **not built or published**; deferred the underlying compatibility feature. The new v2.0.0 development program is planned separately and must pass all roadmap qualification gates.

---

## V2 decision record — 2026-10-25

**HISTORICAL 2026-10-25 DECISION — APPROVED / PLANNED; implementation had not started at that time.** Current progress is recorded in §8 and RESUME HERE. Authorized v2.0.0 development with scope, exit gates, licensing and deferrals recorded in [ROADMAP_V2.md](ROADMAP_V2.md). All v1 implementation and verification claims remain unchanged.

- **Five pillars:** Context Workshop, Project Library, Caveman Mode, Knowledge Generator, and Document Maintainer.
- **Context Workshop:** independent selection model; message-safe fractional and disconnected ranges; Ctrl-drag adds, subsequent ordinary drag replaces; direct `arrow-up-right` before the existing part-copy icon appends to ephemeral Scratchpad with Undo and no window/clipboard disruption.
- **Projects/documents:** optional persistent local profiles, SQLite/FTS5 metadata, independently editable Markdown documents, multi-conversation immutable source snapshots, entire conversation as default AI/document scope, user-controlled standalone or linked outputs.
- **Local AI:** user-level globally shared Ollama runtime and model store, initial Qwen3.5 benchmarking; LangGraph as sole orchestrator, Pydantic as typed contracts, scoped tools and manual approval for all persistent writes. Models never bundled in the executable or venv; no paid/cloud requirement.
- **Crucial bootstrap rule:** **NO AI required for hardware inspection or model recommendation**. At optional first AI use, deterministic target-machine RAM/VRAM/CPU/disk/runtime checks determine suggested models. The portable build cannot know destination hardware. User must consent before installation or download; no-AI use remains fully functional.
- **Generation:** source-grounded TL;DR, high-level/detailed summaries, resume context, Project Record, PRD/TRD/SRS/SDD, decisions, history and handoffs; reported work is not independently verified work.
- **Maintenance:** compare existing authorized document with new evidence; flag conflicts, show reviewable section-level diff, preserve history; verify file hash and require approval before atomic writes.
- **Reuse/license policy:** prioritize permissive MIT/Apache/BSD/ISC/CC0 and tested small components; restrictive/no-license code is not copied without explicit license review. Listed repositories are evaluation candidates, not production dependencies.
- **Sequence:** docs first, Stage 1A Scratchpad arrow, Stage 1B selection core, Stage 1C timeline, then library, model-free Caveman setup, evidence, summaries, documents, document maintainer and packaged qualification.

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

Removed the empty `ExtractAIResponse` source directory manually after relocation.

---

## Phase — Current Maintenance State

**HISTORICAL v1 MAINTENANCE STATE**

YOINK v1.0.0 remains released and stable, with evidence-driven maintenance only. This is **historical v1 release state**; a subsequent 2026-10-25 decision explicitly approved a new v2.0.0 development program under [ROADMAP_V2.md](ROADMAP_V2.md). At that historical point no v2 code was implemented; the subsequent Stage 1A outcome is recorded in §8 and the current-state sections.

---

## Phase — Project/Codex Share Compatibility Research (2026-10-25–26)

**INVESTIGATED / DEFERRED / NO IMPLEMENTATION**

Phases A–A4 established standard-share extraction under unchanged production code; anonymous browser protection responses for Project/Codex links; and visible authenticated access to structured Project conversation data through an in-page query cache. They did not establish full source completeness or a safe production adapter. Closed [Issue #2](https://github.com/kennclark-yb/YOINK/issues/2) after deferring support. No version changes, source edits, commits, pushes, tags or release resulted from the Codex investigations. See §11 for detailed evidence and unresolved constraints.

---



## Task B accepted checkpoint — 2026-11-03 Philippine local time

**IMPLEMENTED / VERIFIED IN DEVELOPMENT / CHECKPOINTED.** Adopted production blue CRT shutdown with two-line SYSTEM / SHUTDOWN lettering, animated scan and one randomized quip. Preserved inactive legacy `assets/shutdown.gif`. Manual Windows close test and independent audit passed. Committed and synchronized checkpoint `7de0613309d977b3e5df0523ea05e2e882662454`. Reported regression: 178 passed, 2 expected skips; 13 native tests per Qt scale. Packaged v2 EXE remains untested.

## Stage 2 design direction — 2026-11-03

**PLANNED / NOT IMPLEMENTED.** Reframed Project Library into **Lorekeeper**, a project-directory-first documentation workflow: discover target documents, confirm selection, reconcile actual code and transcript evidence, preview section-level changes and save only specifically approved edits. When documents are missing, inspect relevant codebase structure and offer to generate necessary docs. Obsidian is an optional editor, not a dependency.

**Designed AI integration to remain provider-neutral.** No-AI scanning/export remains available. Local Caveman/Ollama is optional; future Codex, Claude and other providers require separate supported adapter, explicit connection, privacy/cost notice and tests. AI must not control file writes.

**Document voice:** concise, subjectless developer-authored outcomes. Keep historical audit attribution in evidence files.

# RESUME HERE

**Baseline:** v1.0.0 released; v2 Stage 1A, Option 3, Stage 1B, Stage 1C and Task B checkpointed. Latest published feature-branch commit: `7de0613309d977b3e5df0523ea05e2e882662454`.

**Locked:** Original cobalt-grain artwork, organic connected panels, 84% opacity, spacing, native drag/hover fix, source-preserving extraction, Scratchpad notifications, Parts Picker/Preview and blue CRT shutdown.

**Deferred:** Cell division after failed prototypes; Project-shared and Codex snapshot extraction compatibility.

**Next:** Stage 2 Lorekeeper project-directory scan and document discovery; optional provider-neutral AI/document drafting remains planned and unimplemented.

**Release/verification:** v2 remains development software; no packaged EXE test or v2 release. v1.0.0 remains published. Retain documented Scratchpad paragraph-break limitation and source-validation gaps.

**Preservation:** Keep separate feature worktree, protected original checkout and its 28 diagnostics untouched. No unapproved Git operations, uploads or writes. Successor TPM Task 4 remains incomplete.

**Writing convention:** “Adopted blue CRT shutdown design.” “Deferred cell division after the prototypes failed visual review.” “Designed AI integration to remain provider-neutral.” No “we”, “the owner”, “the user” or model-credit narration in project-facing documents.
