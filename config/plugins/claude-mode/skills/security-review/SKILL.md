---
name: security-review
description: >-
  Security review of pending changes or given code. Use when the user asks for a "security review",
  "/security-review", "is this safe", "check for vulnerabilities", or before exposing code to untrusted input.
---

# Security Review

Scope: uncommitted changes (`git diff`, `git diff --staged`), else the branch vs its base (`git diff <base>...HEAD`),
or the files/PR the user names.

1. Map the attack surface: where untrusted data enters (HTTP params, files, env, CLI args, IPC, DB rows, LLM output)
   and where it lands (shell, SQL, HTML, file paths, deserializers, eval, network calls, logs).
2. Read each changed hunk **with its surrounding code** and trace untrusted data to the sink. Check for:
   - Injection: shell/command, SQL/NoSQL, template, LDAP, prompt injection into tool-using agents
   - XSS / unsafe HTML, open redirects, SSRF, path traversal, unsafe file permissions
   - AuthN/AuthZ gaps: missing checks, IDOR, privilege escalation, broken session/token handling
   - Secrets in code, logs, error messages, or committed config; weak crypto; predictable randomness/temp files
   - Unsafe deserialization, `eval`/`exec`, dependency or supply-chain risks (new packages, curl | sh)
   - DoS: unbounded loops/allocations/regex on user input
3. **Verify every finding** with a concrete exploit path (input → sink → impact). Drop anything you can't
   substantiate. Theoretical style issues are not findings.

Report, most severe first:

```
N. [HIGH|MEDIUM|LOW] path/file.ext:LINE — vulnerability in one sentence
   Exploit: concrete input/steps → impact
   Fix: minimal change
```

If nothing survives, say "No exploitable issues found" and list what you checked. Only help with defensive work
and authorized testing.
