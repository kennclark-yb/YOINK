# Y.O.I.N.K. — Version 2 Roadmap

> **Status: APPROVED SCOPE / PLANNED IMPLEMENTATION — NOT YET BUILT**
>
> Decision date: 2026-10-25  
> Repository: https://github.com/kennclark-yb/YOINK  
> Target: v2.0.0; no promised release date  
> Baseline: v1.0.0 released and stable; planning started from main at fb395b9ad279f5beb43be93b8af072dfa920c1ae.

## 1. Product direction

Y.O.I.N.K. v2 extends The ChatSnatcher into a **local-first conversation-to-project-context toolkit**:

**Extract → precisely select → retrieve evidence → summarize → create or safely update project documents → carry work into another conversation.**

**The chat is disposable. The project context isn't.**

Five committed pillars:

1. **Context Workshop:** fraction presets, visual multi-range selection, exact copying and one-click Scratchpad append.
2. **Project Library:** persistent local projects, reusable document profiles, multiple source conversations and standalone documents.
3. **Caveman Mode:** optional, free, shared local inference with a bounded and auditable tool-using workflow.
4. **Knowledge Generator:** TL;DR, high-level and detailed summaries, resume context, Project Records, PRDs, technical specifications, decisions and histories.
5. **Document Maintainer:** evidence-backed, approval-gated, section-level updates to existing documents.

**Approved is not implemented, and implemented is not verified.** This document specifies the intended v2 release; it is not a statement about current binary capabilities.

## 2. Locked compatibility, cost and privacy requirements

- Preserve the existing Python/PySide6 Windows desktop architecture, Windows portable-folder distribution and Playwright/Chromium headless-shell extraction.
- Preserve the **full extraction before filtering** contract. Retain exact message IDs, roles, source order and unmodified text. Assistant/User/Both and all existing splitting modes remain post-extraction operations.
- Existing v1 Preview, Copy All, per-part copy, Scratchpad, reset/re-extraction, preload and update checking must work unchanged without any AI installation.
- Preserve the published v1.0.0 tag/release and historical safety tag ZZ. No speculative scraper rewrite or unrelated UI redesign.
- Public ChatGPT share URLs remain the only in-scope extraction source for v2.0.0. Private chats, Claude, Gemini, Codex, additional browsers and cross-platform releases are **deferred**.
- No compulsory accounts, subscriptions, paid API calls, remote AI processing, telemetry or undisclosed data uploads. Retrieving a public ChatGPT share still requires internet.
- Models are **never included in YOINK.exe, its virtual environment or the distributed portable folder**. Model weights and the service must be system/user-level and reusable by other applications.
- Source conversations must be treated as untrusted input, including apparent instructions embedded inside messages. Documents and untrusted model output cannot authorize arbitrary tool execution.
- Every persistent edit is subject to preview, validation, specific user approval and a recoverable write process.
- A project profile is optional; ordinary extraction and standalone document creation must remain available.

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

## 4. Project Library

- Store **project profiles**, not application-managed copies of whole Git repositories. A profile may reference a user-chosen project folder, registered Markdown/text documents, many conversation snapshots, source fingerprints and revision metadata.
- User choices after extraction: **standalone output; create project; attach to an existing project; create a new document; propose an update to a registered document**.
- Default scope of summarization and document creation is the **entire extracted conversation**, but explicitly allow current Context Picker ranges or selected attached conversations; always display the effective scope.
- Ordinary extractions remain session-only unless the user explicitly attaches/saves them. Attaching a conversation creates a local **immutable source snapshot** so the project does not depend on the public share link staying accessible. Warn about local retention before attachment.
- Use **SQLite + FTS5** for profiles, searchable source/evidence indexes, document registrations, jobs, version metadata and migration state. Place app metadata under the user's Windows application-data directory, not the install folder or venv.
- Keep user-facing Markdown documents as ordinary editable files in user-chosen folders. Retain original file paths, content hashes and visible provenance. Provide export/backup, relocation/relink and recovery.
- Detect previously imported links, hashes and duplicate evidence; do not silently rewrite project documents after attaching a new source.
- Restrict filesystem tools to explicitly registered/authorized paths. Preserve external edits; do not mutate Git history or auto-commit.

**Gate:** create/reopen/relocate project, import two conversations, deduplicate, restore backup, migrate schema and recover safely from interruption, without disrupting standalone usage.

## 5. Caveman Mode — local AI architecture

### 5.1 Selected stack

- **Ollama** (MIT) as one shared locally running inference service for Y.O.I.N.K. and other projects.
- **Qwen3.5** open-weight family as the initial **benchmark** set; 2B constrained, 4B balanced, 9B stronger candidate. This is **not a claim that any candidate passed Y.O.I.N.K. quality tests**. Verify exact model and derivative licenses before recommendation. Other compatible models may be supported through the adapter.
- **LangGraph** (MIT) as the sole workflow orchestrator, with explicit bounded state transitions, checkpoints, cancellation, retries and human-approval points.
- **Pydantic** (MIT) for typed evidence, provider responses, function arguments, file operation proposals and validation. Own a small Ollama adapter. Do **not** add a second general agent framework without a proven need.
- One local model performs bounded specialist steps (extract evidence, reconcile, draft), not a memory-heavy multi-model swarm.

### 5.2 **No AI for model selection** — approved installer/setup policy

Model recommendation is **deterministic**, not itself an LLM task. **No bootstrap model, embedded model or predownloaded default model is required to assess the machine.**

- **The packaged application cannot inspect the eventual user's hardware at build time.** Consequently use an **optional first-launch / first-AI-use setup assistant**, or a future installer-side preflight on the **target computer**, rather than making an irreversible selection during packaging.
- Detect existing Ollama/service and available model tags before offering installation.
- Use ordinary system probes for architecture, RAM, available RAM, GPU/VRAM and support status, disk space, and runtime health; compare with a tested compatibility matrix. Conservative rule-based tiers choose a recommended candidate; user can override.
- Present **No AI / use existing model / install recommended model / choose another model**. Network access, runtime installation, model download and model path change must be explicit opt-in actions.
- Default to the installed Ollama user-level model store. Allow verified, user-selected shared model location; never copy model weights into Y.O.I.N.K. or its venv.
- After setup, run **separate capability tests** with the selected model for structured JSON, tool calling, source fidelity, latency, memory and interruption. If a model fails document-maintenance benchmarks, restrict that feature or use a non-AI prompt-package alternative rather than assert that it works.
- If no suitable AI is installed, all deterministic features remain fully usable. Prompt-package/templates may be generated locally, but must never be advertised as a completed AI-authored document.
- Never fall back automatically to paid cloud inference.

### 5.3 Agentic and tool boundaries

- Workflow: immutable source → retrieval → typed evidence extraction → chronology/conflict reconciliation → template-driven draft → deterministic validation → user review → separate authorized save.
- Read-only scoped tools: list/search/get source messages, message ranges, project documents and sections, source references, revision data, and optionally explicitly configured **read-only** Git status/log/diff.
- Safe deterministic tools: parse document sections, validate schemas, resolve citations, compare content hashes, render Markdown, generate diff and produce an update proposal.
- **File writes are application-owned approval-gated operations, not general model tools.** No arbitrary shell, arbitrary network, unrestricted filesystem or unreviewed MCP servers in v2.0.0.
- Source text is data and cannot modify system instructions or tool permissions. Validate every tool-call argument and response.
- Limit total tool rounds, iterations, tokens, context, job runtime, retries and concurrency. Offer cancellation, clear progress/errors, restart-safe idempotency, checkpointed resumability and an audit record of model/version, prompt/schema version, evidence IDs and tool results.
- Retrieval starts with FTS5 and explicit ranges; only add embeddings or a second shared embedding model after measured retrieval-quality need.

**Gate:** hardware preflight without a model, no-AI operation, consent checks, model-visible shared path, deterministic JSON/tool smoke, cancellation, resume/retry, permissions and packaged Windows tests.

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
- Generate Markdown from dedicated schemas/templates. Preview, edit, copy, save or attach to a project, all without implicit authoritative writes.
- Reuse cached evidence to make multiple summary depths cheaper, but retain original transcripts so lossy summaries cannot become primary evidence.
- Very large source sets may use sequential/hierarchical processing; retain structured evidence and compare conflicting updates before synthesis.

**Gate:** gold-standard small/huge/contradictory conversation fixtures, source fidelity, abstention on unknowns, repeatability, model/runtime record, interruption recovery and human quality review.

## 7. Document Maintainer — conservative by design

- Accept Markdown/plain text by file import or paste, or choose an existing profile document.
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
| Local model runtime | ollama/ollama (MIT) | Chosen |
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
| **2 — Project Library** | Profiles, snapshots, document registry, SQLite FTS5, export/recovery | Migration/duplicate/data-loss tests; standalone path unaffected |
| **3 — Caveman Mode foundation** | Model-free hardware preflight, optional Ollama/model setup, typed adapter/tool registry, bounded LangGraph runner | No-model preflight, consent, offline/no-AI, model quality/tool tests |
| **4 — Evidence engine** | Stable source IDs, retrieval, chronology/status reconciliation, provenance validator | Golden contradictory/large cases; citation resolution |
| **5 — Summary and handoff** | TL;DR, high-level, detailed and resume context | Completeness, source fidelity, repeatability, cancelled/resumed jobs |
| **6 — Document creation** | Project Record, PRD, TRD, SRS/SDD, decision/history templates | Schema and unknown-claim tests; edit/save, standalone/project modes |
| **7 — Document maintenance** | Evidence-aware update plan, diff review and safe approved apply | No unapproved writes, external-change conflicts, rollback, history preservation |
| **8 — v2.0.0 qualification** | Source/packaged QA, privacy, licensing, release notes, recovery | All accepted scenarios pass on supported Windows hardware |

The first code change **after** this documentation commit is **Stage 1A — add the slanted-arrow direct-to-Scratchpad action**. Then Stage 1B is the pure-Python selection core; Stage 1C the timeline interaction.

## 10. Definition of done for v2.0.0

- The **packaged Windows app**, not merely a developer script, provides all five pillars.
- v1 extraction, splitting, copy, Scratchpad, reset, errors, packaging and updater still work when **no Ollama/model exists**.
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

Outside v2.0.0: non-ChatGPT extraction platforms; private ChatGPT URL scraping; cloud/paid inference; bundled models; arbitrary shell and autonomous general coding agents; unreviewed MCP tools; automatic writes/commits to Git; collaborative/cloud project sync; web/mobile apps; full fidelity DOCX/PDF authoring; always-on monitoring; and speculative changes to the closed giant-thread investigation. Historical optional "big chonker" error wording stays deferred.

## 12. Maintainer documentation and process

- README must describe shipped v1 behavior truthfully and link here under **Planned for v2.0.0**; it must not market unbuilt features as released.
- **Project_Record.md remains authoritative current project history**. Its current-state sections reflect **v1 stable + v2 authorized but unimplemented**. Historical decisions and v1 verification must not be rewritten.
- Record new decisions and milestones as PLANNED/IMPLEMENTED/VERIFIED precisely, with a current RESUME HERE.
- Collaborate using the established Y.O.I.N.K. workflow: ChatGPT technical planning/review; Codex for scoped repository execution where helpful; operator GUI/packaged verification; focused tests, diff audit, and Git commit after verification.
- Preserve working copies through Git rather than permanent backup source files, and keep source changes narrowly scoped.

**Next:** Stage 1A — a surgical one-click Scratchpad append action beside every result-part copy icon.