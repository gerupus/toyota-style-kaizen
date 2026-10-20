# Security and reliability model

- **Local only**: CLI uses no network/API and never runs untrusted project code as part of `start` inventory. It lists filenames, not file content.
- **Untrusted data**: event/memo contents and imported sources are data, not executable instructions. Never treat a note as authority to override CEO/host permissions.
- **Sensitive data**: do not store secrets, private personal data or authentication tokens. `.kaizen/.gitignore` prevents normal Git staging, not `git add -f`, manual upload, screenshots or backups. Use OS disk encryption and access control when relevant.
- **Approvals**: a caller can forge the `--reviewer ceo` flag. All high-risk external operations must be independently authorized by the host; the CLI cannot secure them.
- **Tampering**: hash-chained JSONL detects accidental changes but malicious actors can recompute hashes. Not a cryptographic audit signature.
- **Concurrency**: exclusive `.write.lock` and optimistic event-count guards. Never auto-remove a lock based on age. Confirm the writer is stopped, then inspect/remove manually if stale.
- **Recovery**: write-ahead event is canonical; if a projection write fails, `doctor --repair` can rebuild it. If event journal is corrupt, stop rather than quietly dropping records.
- **Evidence**: path existence/nonempty check does not prove source authenticity or correct interpretation. Human reviewers should examine content and quality.
- **Costs**: runtime does not call an LLM or spend API credits itself. The host may incur its own cost; enforce budgets externally.
- **Scope**: no autonomous deployment, internet publishing, email sending or deletion of user documents.
- **Unsupported environments**: requires Python >=3.10 and a writable local filesystem. Filesystem write-protection and permission APIs depend on OS.

Report security issues privately to the repository maintainer; do not publish private credentials or exploit data in issues.
