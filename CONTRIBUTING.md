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
    "while I was here" rewrites.
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

A good pull request tells us:

1.  What problem does this solve?
2.  What did you change?
3.  How did you test it?
4.  Is there anything reviewers should pay special attention to?

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

## Feature ideas

Issues and feature proposals are welcome. For large changes, opening an
issue before writing the whole thing is a good idea so nobody spends a
weekend building YOINK Enterprise Blockchain Edition by accident.

## License

By contributing to YOINK, you agree that your contribution will be
licensed under the project's [MIT License](LICENSE).

Keep changes focused. Test your work. Don't break the ChatSnatcher.
