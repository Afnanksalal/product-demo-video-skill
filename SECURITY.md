# Security

This skill executes local Playwright, FFmpeg, ffprobe, Node.js, and Python commands with the permissions of the host agent. Review the repository before installing it and keep the host agent's approval and sandbox controls enabled.

The bundled scripts do not upload media or credentials. Browser capture accesses only the URL and resources required by the supplied capture plan. Credentials should be resolved from runtime environment variables or an explicitly authorized browser profile, never committed to a plan.

Do not use production purchasing, messaging, account-management, or destructive workflows unless the user explicitly authorized those side effects. Prefer sandbox providers and test accounts.

To report a vulnerability, open a private GitHub security advisory for this repository. Do not include real credentials, session files, or private recordings in a public issue.
