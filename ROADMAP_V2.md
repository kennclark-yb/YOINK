# Y.O.I.N.K. — Version 2 Roadmap

> **Status: APPROVED SCOPE / v2 DEVELOPMENT — Stage 1C OWNER-APPROVED BASELINE; NOT A RELEASE**
>
> Decision date: 2026-10-25  
> Repository: https://github.com/kennclark-yb/YOINK  
> Target: v2.0.0; no promised release date  
> Baseline: v1.0.0 released and stable; planning started from main at fb395b9ad279f5beb43be93b8af072dfa920c1ae.

## Current status — 2026-11-03

- **Released:** v1.0.0 remains the only published release; stable main unchanged.
- **Checkpointed:** Stage 1C connected workspace and Task B blue CRT shutdown. Retained the original cobalt-grain background. Deferred cell division after the prototypes failed visual review.
- **Verified:** Manual Windows shutdown test and independent checkpoint audit passed. Task B feature-branch commit: `7de0613309d977b3e5df0523ea05e2e882662454`.
- **Next:** Stage 2 Lorekeeper folder/document discovery; optional provider-neutral AI and actual document generation remain planned, not implemented.
- **Pending:** Packaged v2 EXE, new live-share and broad Windows/hardware testing.

## 1. Product direction

Y.O.I.N.K. v2 extends The ChatSnatcher into a **local-first conversation-to-project-context toolkit**:

**Extract → precisely select → retrieve evidence → summarize → create or safely update project documents → carry work into another conversation.**

**The chat is disposable. The project context isn't.**

Five committed pillars:

1. **Context Workshop:** fraction presets, visual multi-range selection, exact copying and one-click Scratchpad append.
2. **Lorekeeper:** choose an existing project folder, discover relevant documents, inspect codebase evidence, and safely propose updates or new documentation.
3. **Optional AI:** provider-neutral drafting contract; no AI, local Caveman/Ollama or future supported Codex, Claude and other explicit opt-in adapters.
4. **Knowledge Generator:** TL;DR, high-level and detailed summaries, resume context, Project Records, PRDs, technical specifications, decisions and histories.
5. **Document Maintainer:** evidence-backed, approval-gated, section-level updates to existing documents.

**Approved is not implemented, and implemented is not verified.** This document specifies the intended v2 release; it is not a statement about current binary capabilities.

## 2. Locked compatibility, cost and privacy requirements

- Preserve the existing Python/PySide6 Windows desktop architecture, Windows portable-folder distribution and Playwright/Chromium headless-shell extraction.
- Preserve the **full extraction before filtering** contract. Retain exact message IDs, roles, source order and unmodified text. Assistant/User/Both and all existing splitting modes remain post-extraction operations.
- Existing v1 Preview, Copy All, per-part copy, Scratchpad, reset/re-extraction, preload and update checking must work unchanged without any AI installation.
- Preserve the published v1.0.0 tag/release and historical safety tag ZZ. No speculative scraper rewrite or unrelated UI redesign.
- Public ChatGPT share URLs remain the only in-scope extraction source for v2.0.0. Private chats, Claude, Gemini, Codex, additional browsers and cross-platform releases are **deferred**.
- No compulsory AI, accounts, subscriptions, paid calls, telemetry or undisclosed uploads. Remote AI is strictly opt-in with explicit provider choice, source-sharing notice and any cost disclosure. Retrieving a public ChatGPT share still requires internet.
- Models are **never included in YOINK.exe, its virtual environment or the distributed portable folder**. Model weights and the service must be system/user-level and reusable by other applications.
- Source conversations must be treated as untrusted input, including apparent instructions embedded inside messages. Documents and untrusted model output cannot authorize arbitrary tool execution.
- Every persistent edit is subject to preview, validation, specific user approval and a recoverable write process.
- A project profile and AI connection are optional; ordinary extraction and standalone document creation remain available.
- **Document voice:** concise, subjectless developer-authored decisions/status updates: “Adopted blue CRT shutdown design.” “Deferred cell division after the prototypes failed visual review.” “Designed AI integration to remain provider-neutral.” Avoid “we”, “the owner”, “the user” and agent-credit narration in project prose. Keep attribution in separate audit evidence.

## 3. Context Workshop

### 3.1 Direct Scratchpad action — first implementation task

In each Results part card, add a small **slanted arrow / arrow-up-right icon immediately before the existing copy icon**. The existing copy icon must remain unchanged.

- Arrow appends the **original intact part** to this session's Scratchpad in a single click.
- No opening, focusing or closing Scratchpad; no clipboard change; no existing notes erased.
- Include useful source/part identification and an Undo for the most recent append.
- Avoid accidental exact duplicates while allowing deliberate repeats. Test copy/append independence.
- Maintain the current extraction-session lifecycle: Scratchpad is ephemeral; **Extract Another Thread** or closing Y.O.I.N.K. clears it.
- Later allow **Add to Scratchpad** for a selected context range or individual Preview message.
- Scratchpad remains a freeform text area and is **not** the source of truth for the selection model or a project document.

### 3.2 Visual Context Picker

Build a separate Context Picker using a pure-Python range-selection core and a custom PySide6 timeline.

- Fraction presets: final quarter (75–100%), final half (50–100%), final three-quarters (25–100%), first half (0–50%).
- Support a manually specified start/end, individual messages and **multiple disconnected ranges**, not only one continuous slice.
- **Drag** sets a new range and replaces previous selections. **Ctrl+drag** adds a new range while retaining earlier selections. Releasing Ctrl **does not clear** existing selections; the next ordinary drag replaces them.
- Provide adjustable range endpoints, removal, Clear, hover/keyboard interaction, visible message boundaries and an accessible numeric alternative. Show selected count and coverage.
- Default percentage basis: **number of messages**, never partial message text. An optional percentage-of-characters mode may choose the nearest intact message boundary.
- Merge overlapping or adjacent ranges, deduplicate output, preserve chronological order, IDs, original numbering and source metadata.
- Preview before copy/append. Role-filter selection is applied to the output, not the stored full source. Empty/no-match selections must be explained.
- Do not send only the selected portion to Playwright: always extract the full conversation first.

**Gate:** unit tests for odd/even fraction boundaries, long individual messages, range merging, duplicate prevention, role filtering, source numbering; GUI tests for Ctrl behavior, copy, append, Undo, reset and keyboard access.

## 4. Lorekeeper — project-directory-first documentation

**Purpose:** discover and maintain documentation in an existing project folder, rather than replicate a notes library.

### Existing documentation
1. Select an authorized directory; scan read-only by default.
2. Discover candidate README, architecture, design, history, decisions, logs, specifications and other relevant documents from filenames and content.
3. Show paths, document roles and confidence; confirm or adjust targets.
4. Reconcile the full extracted conversation (or explicitly selected ranges) with selected documents, relevant source code, tests and optional read-only Git state. Distinguish claims, decisions, verified code and unknowns.
5. Present section-level, source-linked modifications with individual accept/reject controls; save only approved edits using hash checks, atomic writes and recovery.

### No documentation found
1. Report missing documentation; request approval to generate appropriate files.
2. Inventory the full authorized directory, but inspect code intelligently by project structure, entry points, imports, dependencies, tests and selected relevant files. Exclude secrets, generated artifacts, binaries and dependency trees by default.
3. Build source-referenced compact context packages for lower-capacity models without replacing original transcript/code evidence.
4. Reconcile transcript with production baseline; ask for missing intent, goals, roadmap or rationale only when necessary.
5. Propose suitable README, architecture, project record, ADR, history and other documents; preview and approve targets and writes individually.

### Storage and interoperability
- Keep lightweight optional project profiles, registered document paths, opt-in immutable transcript snapshots, hashes and revision/job metadata; never manage or duplicate the full repository.
- Use SQLite + FTS5 in Windows user app-data for evidence indexing, migration, duplicate detection, recovery and backup. Keep Markdown as normal files in their selected directories.
- Obsidian is an **optional** editor/vault jump point; no required vault or Obsidian installation.
- Without AI, extraction, folder scan, doc discovery and context-package export remain usable. Do not pretend deterministic templates completed AI drafting.

**Gate:** authorized reads, explicit target selection, provenance, deduplication, migrations, recovery, zero unapproved writes and unaffected standalone extraction.

## 5. Optional AI — provider-neutral architecture

### Provider and ownership boundary
- Y.O.I.N.K. owns authorized project scanning, source identity, retrieval, evidence validation, diff review, approval, saving and recovery. Reasoning providers only analyze and draft under a bounded typed adapter.
- Allow **No AI / export context package / local AI / connected supported provider**. Codex, Claude and other external adapters require separately verified API/interface support, authentication, user consent, cost/privacy disclosure and quality tests. Do not presume consumer subscriptions provide API usage or autonomous CLI access.
- Ollama (MIT) remains the first **optional local adapter candidate**, not a required runtime. Qwen3.5 2B/4B/9B remain benchmark candidates only. No model weights bundled with Y.O.I.N.K.
- Pydantic (MIT) validates provider/evidence contracts. LangGraph (MIT) is the planned bounded orchestrator where useful: checkpoints, cancellation, retries, capability/budget limits and manual approval.
- No automatic cloud upload, paid fallback, uncontrolled shell, filesystem, Git, network or unreviewed MCP actions by AI. Treat transcripts and code as untrusted instructions.

### Deterministic local setup
- Detect local runtime/model, CPU, RAM, GPU/VRAM and available disk on the destination device without an AI bootstrap model. Show no-AI and existing-model options before any optional install/download.
- Keep reusable local weights outside the portable app and venv. Require explicit permission for runtime installation, network access, model download or storage changes.
- Validate structured output, source fidelity, evidence references, token/context limits, privacy, latency and interruptions for each supported provider. Disable unsupported drafting operations rather than claiming success.
- Scope read tools to chosen files/messages and optional read-only Git; use FTS5 retrieval before considering embeddings.

**Gate:** no-AI operation, provider independence, user-controlled data transfer, typed contracts, source fidelity, safe cancellation/recovery and packaged Windows tests.

## 6. Knowledge Generator — summaries and documents

### 6.1 Outputs

- **TL;DR:** key outcome and immediate next step in a few sentences.
- **High-level summary:** objectives, phases, decisions, outcomes and outstanding issues.
- **Detailed summary:** themes/chronology, technical constraints and trade-offs, accepted/rejected/superseded decisions, source references and open work.
- **Resume Context:** portable handoff of authoritative current state, locked constraints, important history, verified versus reported work and immediate next steps.
- **Documents:** Project Record, PRD, TRD/Technical Specification, SRS, SDD, ADR/Decision Log, History/Changelog, Handoff or user-supplied Markdown template.

### 6.2 Evidence contracts

- Preserve immutable source messages and IDs plus hashes; derive traceable evidence records and stable references back to specific messages.
- Segment only as required by measured token/memory budgets, including exceptionally long single messages; never silently truncate.
- Extract requirements, decisions, milestones, risks and implementation **claims** from transcript slices; reconcile them with chronology and registered authoritative documents.
- Distinguish **proposed, accepted, reported implemented, externally verified, deferred, rejected, superseded and unknown**.
- A chat statement that tests passed is **not independently verified**. Read-only Git/test evidence, when supplied, is marked with its own origin.
- Important claims must resolve to source messages or be explicitly labeled uncertain; code validates that citations exist and match retained sources.
- Generate Markdown from dedicated schemas/templates in developer voice: concise subjectless outcomes, no “we” or third-person owner/user/agent narration. Preserve provenance in separate audit records. Preview, edit, copy, save or attach to a project, without implicit writes.
- Reuse cached evidence to make multiple summary depths cheaper, but retain original transcripts so lossy summaries cannot become primary evidence.
- Very large source sets may use sequential/hierarchical processing; retain structured evidence and compare conflicting updates before synthesis.

**Gate:** gold-standard small/huge/contradictory conversation fixtures, source fidelity, abstention on unknowns, repeatability, model/runtime record, interruption recovery and human quality review.

## 7. Document Maintainer — conservative by design

- Accept Markdown/plain text by file import/paste, discover candidates in a selected project folder, or choose a registered project document.
- Parse current sections and recognized status/history blocks, compare source-backed new information, and generate proposed **add, change, retain, flag, or supersede** operations.
- Protect accepted decisions, verified information, prior history, manual prose and unaffected sections. An unverified newer chat statement does not override an authoritative recorded fact.
- Show unified/side-by-side diff, evidence links and individual accept/reject controls. Rejecting an edit must not change saved content.
- Verify that the original file hash is still unchanged immediately before writing. On external edits or conflicts, abort and re-review.
- Write only approved modifications via atomic file replacement with recoverable previous revision and audit log. No automatic Git commits.
- Do not claim a Project Record is 'updated' merely because a model generated a new one; approval and saved-file verification are required.

**Gate:** zero unapproved writes, conflict detection, section isolation, history and provenance retention, recovery/rollback and long-project update validation.

## 8. Permissive reuse and licensing

**Reuse-first, not dependency-at-any-cost.** Before vendoring/adapting code verify functional tests, transitive licenses, attribution, packaging, Windows/Python compatibility and model license. MIT, Apache-2.0, BSD, ISC and appropriate CC0 are preferred. GPL/AGPL, Commons Clause, noncommercial and unlicensed code are **not directly copied into MIT Y.O.I.N.K.** without explicit licensing review. Underlying public functional concepts can inform an independently written implementation.

| Need | GitHub reference | Status |
| --- | --- | --- |
| Optional local runtime | ollama/ollama (MIT) | Initial adapter candidate, not required |
| Orchestration | langchain-ai/langgraph (MIT) | Chosen |
| Typed contracts | pydantic/pydantic (MIT) | Chosen |
| Long-document summary | Wintersta7e/Doc-Summarizer (MIT) | First isolated code-evaluation candidate |
| Compare summary approaches | HarshAggarwal242/LocalDoc-AI (MIT) | Reference |
| PRD structure | dredozubov/prd-generator (MIT) | Template/prompt reference |
| Section generation | yoligehude14753/docforge (MIT) | Candidate implementation reference |
| Requirements validation | CRELLIA-S-L/srs-dd (MIT) | Reference for stable IDs and traceability |
| SRS/SDD documents | jam01/SRS-Template and jam01/SDD-Template (CC0) | Preferred template foundations |
| Delta spec changes | Fission-AI/OpenSpec (MIT) | Architectural reference |
| Source-preserving handoff | jugugug/AgentHandoff (MIT) | Provenance reference |
| Persistent knowledge ideas | basicmachines-co/basic-memory (AGPL-3.0) | Reference only; no code copied |
| Decision-history review | Team-Existing/KnowledgeHub (AGPL-3.0) | Reference only; no code copied |

No candidate summarizer or generator is a production dependency until a small controlled spike proves its independent use, quality and license fit. If evaluation fails, implement a focused native Python component under the same contracts. Avoid adopting unnecessary Docker stacks and separate web UIs.

## 9. Ordered development and exit gates

Each phase is a bounded reviewable change with its own tests, checks and stable Git checkpoint. Do not interleave unrelated features.

| Stage | Deliverable | Required exit gate |
| --- | --- | --- |
| **0 — Documentation and baseline** | Publish roadmap; synchronize README/Project Record; preserve v1 history | Consistent planned statuses; only docs changed; links verified |
| **1 — Context Workshop** | Scratchpad arrow + Undo, selection core, timeline Ctrl-drag, fraction presets, selection copy/append | Deterministic range tests and GUI clipboard/reset checks |
| **2 — Lorekeeper foundation** | Scoped directory scan, doc discovery, lightweight profiles, SQLite FTS5, recovery | Authorization, migration/duplicate/data-loss tests; standalone path unaffected |
| **3 — Optional AI foundation** | Provider-neutral adapters, no-AI context export, optional local Ollama benchmark and separately gated external providers | No-AI, consent, adapter isolation, schema and quality tests |
| **4 — Evidence engine** | Stable source IDs, retrieval, chronology/status reconciliation, provenance validator | Golden contradictory/large cases; citation resolution |
| **5 — Summary and handoff** | TL;DR, high-level, detailed and resume context | Completeness, source fidelity, repeatability, cancelled/resumed jobs |
| **6 — Document creation** | Project Record, PRD, TRD, SRS/SDD, decision/history templates | Schema and unknown-claim tests; edit/save, standalone/project modes |
| **7 — Document maintenance** | Evidence-aware update plan, diff review and safe approved apply | No unapproved writes, external-change conflicts, rollback, history preservation |
| **8 — v2.0.0 qualification** | Source/packaged QA, privacy, licensing, release notes, recovery | All accepted scenarios pass on supported Windows hardware |

Stage 1A — the slanted-arrow direct-to-Scratchpad action — is completed, tested, owner accepted, and locally committed. Stage 1B pure-Python selection core is locally checkpointed; Stage 1C timeline and connected workspace are implemented and owner-approved. Task B shutdown-screen redesign precedes Stage 2 Project Library in the current working sequence.

## 10. Definition of done for v2.0.0

- The **packaged Windows app**, not merely a developer script, provides all five pillars.
- v1 extraction, splitting, copy, Scratchpad, reset, errors, packaging and updater still work with **no AI provider**.
- Fraction selection and disconnected Ctrl-drag ranges are precise, deduplicated, previewable, correctly numbered and keyboard accessible.
- Direct Scratchpad append takes one click, preserves clipboard and session notes, and has Undo.
- A project can retain at least two imported conversations and create/update a linked document with source traceability.
- Optional hardware assessment runs entirely without AI before deciding on a download; installed models are globally reusable outside Y.O.I.N.K.
- Source-backed summaries and documents distinguish recorded claims from independent verification; long-thread truncation and unsupported claims fail review.
- Updates are reviewable and never write without approval and unchanged-target verification.
- Tests cover duplicates, schema migrations, offline behavior, malformed source/model responses, interruption, recovery, security, file permissions and package smoke.
- Dependency, weight and copied asset licenses are independently recorded with notices. User documentation explains model storage and local privacy.
- No release designation until complete tests and manual packaged QA pass. Intermediate stages are development milestones, **not automatic stable releases**.

## 11. Explicit deferrals

Outside v2.0.0: non-ChatGPT extraction platforms; private ChatGPT URL scraping; automatic/undisclosed cloud or paid inference; unverified direct Codex/Claude integrations; bundled models; arbitrary shell and autonomous general coding agents; unreviewed MCP tools; automatic writes/commits to Git; collaborative/cloud project sync; web/mobile apps; full fidelity DOCX/PDF authoring; always-on monitoring; and speculative changes to the closed giant-thread investigation. Historical optional "big chonker" error wording stays deferred.

## 12. Maintainer documentation and process

- README must describe shipped v1 behavior truthfully and link here under **Planned for v2.0.0**; it must not market unbuilt features as released.
- **Project_Record.md remains authoritative current project history**. Checkpointed Stage 1A, Option 3, Stage 1B, Stage 1C and Task B; Stage 2 Lorekeeper planned. Preserve historical facts and v1 verification.
- Record new decisions and milestones as PLANNED/IMPLEMENTED/VERIFIED precisely, with a current RESUME HERE. Use subjectless developer-style decisions and impersonal Git commit subjects; reserve person/tool attribution for audit evidence.
- Collaborate using the established Y.O.I.N.K. workflow: ChatGPT technical planning/review; Codex for scoped repository execution where helpful; operator GUI/packaged verification; focused tests, diff audit, and Git commit after verification.
- Preserve working copies through Git rather than permanent backup source files, and keep source changes narrowly scoped.

**Current checkpoint:** Retained Option 3 background and connected Stage 1C workspace. Adopted and checkpointed Task B blue CRT. Deferred cell division. Planned Lorekeeper as the next stage, with optional provider-neutral AI. Packaged v2 testing remains pending.
