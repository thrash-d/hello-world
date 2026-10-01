# Backlog

Changes considered and declined, with the reason.

- Drop the OS error text from the stderr message: the review rated it acceptable, and the errno is what someone debugging a dead stdout needs.
- Support Python 2 or versions before 3.6: f-strings already fail closed with a `SyntaxError`, which the review rated fine.
- Deployment controls from the review's medium section, such as a locked-down install path and a pinned interpreter: these are rollout steps for the workstations, not code changes.
