# Contributing to YOINK

Thanks for wanting to improve the ChatSnatcher.

Bug reports, ideas, fixes, and focused improvements are welcome. The
goal is to keep YOINK small, dependable, understandable, and difficult
to accidentally murder.

## Before opening a pull request

-   Keep the change focused. One pull request should solve one coherent
    problem.
-   Explain what changed and why.
-   Test the behavior you changed.
-   Run the existing relevant tests and make sure they still pass.
-   Add or update tests when the change introduces behavior that should
    be protected from regression.
-   Avoid unrelated refactors, formatting sweeps, dependency churn, or
    opportunistic drive-by rewrites.
-   Do not include private ChatGPT conversations, credentials, tokens,
    personal data, generated build folders, or other sensitive/test
    material.

## Security-sensitive changes

Changes involving URL handling, browser automation, external requests,
update behavior, packaging, file access, or anything else with security
implications deserve extra scrutiny.

Please describe the security impact in the pull request and avoid
weakening validation or trust boundaries merely to make something work.

If you believe you found a security vulnerability, do not publish
sensitive exploit details in a public issue. Contact the maintainer
privately through an available GitHub contact method first.

## Tests

The automated test suite lives under `tests/`.

Use the project's pinned dependencies and run the relevant tests for
your change. A pull request should not knowingly leave existing tests
broken.

Packaging or GUI changes may also require manual verification because
not every interaction is meaningfully testable through automation.

## Pull requests

A useful pull request description records:

1.  What problem does this solve?
2.  What did you change?
3.  How did you test it?
4.  Which limitations, risks, or unverified cases remain?

Screenshots are useful for visible GUI changes.

Opening a pull request does not guarantee that it will be merged.
Changes may be declined because of scope, maintenance cost, project
direction, security concerns, or because the fat bastard simply does not
need that many buttons.

## Style

Match the existing code and project structure unless the change
specifically requires otherwise.

Prefer boring, readable code over clever code.

Do not introduce a new dependency when a small existing solution will
do.

## Documentation, Git, and audit writing

Use **concise, impersonal, developer-authored wording** in project records,
architectural decisions, README updates, commit subjects and bodies, pull
requests, changelogs, release notes, and **audit summaries**.

-   Lead with the outcome or action. Examples: `Adopted blue CRT shutdown design`;
    `Deferred cell division after unsuccessful visual prototypes`;
    `Designed provider-neutral AI integration`.
-   Avoid “we”, “I”, “the user”, “the owner”, and unnecessary references to
    Codex, ChatGPT, reviewers, agents, or approval conversations. Explain
    the implementation, decision, evidence, and next action instead.
-   Keep commit messages short and descriptive, using verbs such as
    `Add`, `Fix`, `Retain`, `Refactor`, `Document`, or `Verify`.
    Do not rewrite existing published commits merely to change their wording.
-   Use the same tone for pull request titles and descriptions. Record scope,
    tests, remaining limitations, and evidence without narrating who did what.
-   Write release notes and changelogs as user-relevant changes with
    precise implementation/verification status. Never present planned work
    as shipped functionality.
-   Summarize audits as **Status / Changes / Checks / Evidence / Limitations**.
    Example: `Validation: 178 passed, 2 expected skips; packaged EXE not tested.`
-   When execution identity materially affects reproducibility, retain it as
    technical metadata in the full audit log (`Executor`, `Environment`,
    `Tool/version`, `Commit SHA`, `Evidence path`), not as the narrative voice.
    Preserve source provenance, honest uncertainty, and reported-versus-
    independently-verified distinctions.

Historical published releases, Git commit history, and original audit
artifacts are evidence: **do not alter them solely to normalize wording**.
Apply this convention to new writing and correct stale current-status text.

## Feature ideas

Issues and feature proposals are welcome. For large changes, opening an
issue before writing the whole thing is a good idea so nobody spends a
weekend building YOINK Enterprise Blockchain Edition by accident.

## License

By contributing to YOINK, you agree that your contribution will be
licensed under the project's [MIT License](LICENSE).

Keep changes focused. Test your work. Don't break the ChatSnatcher.
