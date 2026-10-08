#!/usr/bin/env python3
"""Strict PreToolUse guard for agy (toolPermission=always-proceed). Deterministic, no model calls.

allow   -> safe, in-scope work runs instantly
confirm -> denied until the user's latest message approves it ("yes", "go ahead", or the exact command);
           one approval covers one action
never   -> catastrophic; the user must run it themselves
"""
import hashlib
import json
import os
import re
import sys
import time

HOME = os.path.expanduser("~")
STATE = os.path.join(HOME, ".cache", "agy-guard")
LOG = os.path.join(STATE, "decisions.jsonl")
MAX_SCRIPT = 400_000

NEVER = [
    (r"\brm\s+(-\S+\s+)*(--no-preserve-root\s+)?(/|/\*|~|~/|~/\*|\$HOME|\$HOME/|\$HOME/\*|\"\$HOME\")(\s|;|&|\||$)",
     "deletes the root or home directory"),
    (r"--no-preserve-root", "disables rm's root protection"),
    (r"\bmkfs(\.\w+)?\b|\bwipefs\b", "formats or wipes a filesystem"),
    (r"\bdd\b[^|;&]*\bof=/dev/", "writes raw data to a device"),
    (r">\s*/dev/(sd|nvme|mmcblk|disk|vd|hd)", "overwrites a block device"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "fork bomb"),
    (r"\bchmod\s+(-\S+\s+)*[0-7]?777\s+/(\s|$)|\bchown\s+-R\s+\S+\s+/(\s|$)", "changes permissions of the whole system"),
]

CONFIRM = [
    # destructive
    (r"\brm\s+(\S+\s+)*(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b", "recursive delete"),
    (r"\brm\s+[^|;&]*\*", "wildcard delete"),
    (r"\bfind\b[^|;&]*\s-(delete|exec\s+rm|execdir\s+rm)", "find that deletes files"),
    (r"\b(shred|truncate)\s", "destroys file contents"),
    (r"\bgit\s+(\S+\s+)*clean\s+(\S+\s+)*-[a-zA-Z]*f", "git clean deletes untracked files"),
    (r"\bgit\s+(\S+\s+)*reset\s+(\S+\s+)*--hard", "git reset --hard discards work"),
    (r"\bgit\s+(\S+\s+)*(checkout|restore)\s+(\S+\s+)*(--\s+)?\.(\s|$)", "discards uncommitted changes"),
    (r"\bgit\s+(\S+\s+)*branch\s+(\S+\s+)*(-D|--delete\s+--force)", "force-deletes a branch"),
    (r"\bgit\s+(\S+\s+)*stash\s+(drop|clear)", "drops stashed work"),
    (r"\bgit\s+(\S+\s+)*(rebase|filter-branch|filter-repo)\b", "rewrites git history"),
    (r"\bgit\s+(\S+\s+)*commit\s[^|;&]*--amend", "amends a commit"),
    (r"--no-verify\b", "skips git hooks"),
    (r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b", "drops database data"),
    (r"\bdocker\s+(system\s+prune|volume\s+(rm|prune)|rm\s+-f)", "deletes docker data"),
    # publishing / affecting others
    (r"\bgit\s+(\S+\s+)*push\b", "git push publishes to a remote"),
    (r"\bgh\s+(pr|issue|release|repo|gist)\s+(create|merge|close|comment|edit|delete|review|fork)", "GitHub action visible to others"),
    (r"\b(npm|pnpm|yarn|cargo|twine|poetry|uv)\s+publish\b", "publishes a package"),
    # remote / untrusted code execution
    (r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(ba|z|da|fi)?sh\b", "pipes a downloaded script into a shell"),
    (r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(python\d?|perl|ruby|node)\b", "pipes downloaded code into an interpreter"),
    (r"<\(\s*(curl|wget)\b", "runs a downloaded script"),
    (r"base64\s+(-d|--decode)[^|;&]*\|\s*(ba|z)?sh|\bxxd\s+-r[^|;&]*\|\s*(ba|z)?sh", "runs obfuscated code"),
    (r"(^|[;&|]\s*)eval\s", "eval of dynamic code"),
    (r"\$\([^)]*base64\s+(-d|--decode)|`[^`]*base64\s+(-d|--decode)", "runs obfuscated code"),
    (r"(^|[;&|(]\s*)\"?\$\{?[A-Za-z_]\w*\}?\"?\s", "runs a command hidden in a variable"),
    # indirect deletes / overwrites
    (r"\bxargs\s+(\S+\s+)*(rm|unlink|shred|rmdir)\b", "deletes files via xargs"),
    (r"\bmv\s+[^|;&]*\s/dev/null\b|\bcp\s+/dev/null\s", "destroys a file via /dev/null"),
    (r"\brsync\b[^|;&]*--delete", "rsync --delete removes files"),
    (r"\bdd\s", "raw data copy with dd"),
    (r"\b(npx|bunx|uvx|pipx)\s|\bpnpm\s+dlx\b", "downloads and runs a package"),
    (r"\b(cargo|go)\s+install\b|\bnpm\s+(i|install)\s+(\S+\s+)*-g\b", "installs a global tool"),
    (r"\bpip3?\s+install\s+(?!(-r\s|--requirement\s|-e\s+\.|\.\s*$|\.\[))", "installs a Python package"),
    (r"\b(npm|pnpm|yarn|bun)\s+(add|install|i)\s+(?!-)\S", "adds a new JS dependency"),
    # system level
    (r"(^|[;&|(]\s*)(sudo|doas|su|pkexec|run0)\b", "runs as root"),
    (r"\b(pacman|yay|paru)\s+-(S|R|U)", "installs or removes system packages"),
    (r"\bsystemctl\s+(--user\s+)?(enable|disable|start|stop|restart|mask|unmask|daemon-reload|edit)", "changes system services"),
    (r"\b(mkinitcpio|limine-mkinitcpio|grub-install|grub-mkconfig|bootctl|efibootmgr)\b", "changes boot configuration"),
    (r"\b(reboot|poweroff|shutdown|halt)(\s|$)|\bsystemctl\s+(reboot|poweroff|suspend|hibernate)", "reboots or powers off"),
    (r"\b(fdisk|parted|sgdisk|gdisk|cryptsetup|mount|umount|swapon|swapoff)\b", "disk or mount operation"),
    (r"\b(ufw|iptables|nft|firewall-cmd)\b", "changes the firewall"),
    (r"\b(usermod|useradd|userdel|passwd|visudo|chsh)\b", "changes users or auth"),
    (r"\bcrontab\s+-(e|r)|\bat\s+now", "schedules persistent jobs"),
    (r"\bchmod\s+(-\S+\s+)*([0-7]?777|[ugoa]*\+s|-R)\b|\bchown\s+-R\b", "risky permission change"),
    (r"\b(kill|pkill|killall)\s", "kills processes"),
    (r"\bdocker\s+run\b[^|;&]*(--privileged|-v\s+/:)", "privileged container"),
    # network: sending data / exposing machine
    (r"\b(curl|wget)\b[^|;&]*\s(-d|--data\S*|-F|--form|-T|--upload-file|-X\s*(POST|PUT|PATCH|DELETE)|--post-data|--post-file)\b",
     "sends data to a remote server"),
    (r"\b(nc|ncat|netcat|socat|telnet)\s", "raw network connection"),
    (r"\b(scp|sftp|ftp)\s|\brsync\b[^|;&]*\S+@?\S+:\S*|\bssh\s", "remote copy or login"),
    (r"\b(python3?\s+-m\s+http\.server|php\s+-S|ngrok|cloudflared|localtunnel)\b", "exposes files or ports"),
]

SECRET = re.compile(
    r"(\.ssh/|\.gnupg|\bid_(rsa|ed25519|ecdsa|dsa)\b|oauth_creds|credentials(\.json)?\b|\.netrc|\.password-store|"
    r"keyring|\.aws/|\.kube/config|\.docker/config|google_accounts\.json|\.git-credentials|\bprintenv\b|"
    r"(^|[;&|]\s*)env\s*($|[;&|])|/proc/\d+/environ)"
)
OFF_TASK = re.compile(r"(\.claude/|\.claude$|\.codex/|\.cursor/|\.gemini/antigravity(-cli)?/(brain|conversations)/|"
                      r"\.config/(google-chrome|chromium|BraveSoftware)/|\.mozilla/)")
CONTROL = [os.path.join(HOME, p) for p in (".gemini/config", ".gemini/antigravity-cli/settings.json",
                                           ".gemini/settings.json", ".cache/agy-guard")]
CONTROL_RX = re.compile(r"\.gemini/(config|antigravity-cli/settings\.json|settings\.json)|agy-guard")
SENSITIVE_WRITE = re.compile(r"(^|/)(\.bashrc|\.bash_profile|\.zshrc|\.profile|\.zprofile|authorized_keys|"
                             r"\.gitconfig)$|(^|/)\.git/|^/(etc|usr|boot|opt|var|root)/")
WRITE_OK_OUTSIDE = [os.path.join(HOME, ".config"), "/tmp"]

SCRIPT_RX = [
    (r"shutil\.rmtree|os\.(remove|unlink|rmdir)\s*\(|Path\([^)]*\)\.(unlink|rmdir)\(", "deletes files"),
    (r"os\.system\s*\(|subprocess\.[a-zA-Z_]+\([^)]*shell\s*=\s*True|os\.popen\(", "runs shell commands"),
    (r"requests\.(post|put|patch|delete)\s*\(|urlopen\([^)]*data=|httpx\.(post|put)|\.sendall\(|socket\.socket\(",
     "sends data over the network"),
    (r"\b(exec|eval)\s*\(\s*(requests|urllib|base64|compile|__import__|bytes|codecs)", "executes dynamic or downloaded code"),
    (r"child_process|\.(rmSync|rmdirSync|unlinkSync)\s*\(|\bfs(/promises)?['\"]?\)?\.(rm|unlink|rmdir)\s*\(|"
     r"\b(execSync|spawnSync)\s*\(", "runs commands or deletes files"),
    (r"os\.removedirs|os\.rename\([^)]*/dev/null|send2trash|\.write_text\(\s*['\"]{2}\s*\)", "deletes or wipes files"),
    (r"ctypes\.|pty\.spawn", "low-level system access"),
    (r"subprocess\.\w+\(\s*\[\s*[\"'](rm|sudo|git|curl|wget|pacman|dd|chmod|kill|pkill)[\"']", "runs risky commands"),
    (r"[\"'][^\"'\n]*\b(rm\s+-[a-zA-Z]*[rR]|git\s+push|sudo\s|pacman\s+-[SRU]|(curl|wget)[^\"'\n]*\|\s*(ba|z)?sh)",
     "embeds a risky shell command"),
]
SHELL_EXT = (".sh", ".bash", ".zsh")
INLINE = re.compile(
    r"\b(python\d?(\.\d+)?|node|deno|bun|perl|ruby|php|osascript)\s+(\S+\s+)*(-c|-e|-p|-r|--eval|--print|eval)(\s|$)|"
    r"\b(python\d?(\.\d+)?|node|perl|ruby|php|bash|sh|zsh|fish)\s+-(\s|$)|"
    r"\|\s*(python\d?(\.\d+)?|node|perl|ruby|php|deno|bun)(\s*$|\s*[;&|)]|\s+-)|"
    r"<<-?\s*['\"]?\w+"
)
READ_ONLY_TOOLS = {"view_file", "search_web", "ask_question", "manage_subagents"}
INTERP = re.compile(r"(^|[;&|]\s*|\s)(sudo\s+)?(python\d?(\.\d+)?|bash|sh|zsh|fish|node|deno|bun|perl|ruby|php|"
                    r"tsx|ts-node)\s+((?:-\S+\s+)*)([^\s;&|<>]+\.(py|sh|bash|zsh|js|mjs|cjs|ts|pl|rb|php))\b")
DIRECT_SCRIPT = re.compile(r"(^|[;&|]\s*)(\./|/|~/)([^\s;&|<>]+\.(py|sh|bash|zsh|js|mjs|pl|rb))\b")


def args_of(payload):
    tc = payload.get("toolCall") or {}
    out = {}
    for k, v in (tc.get("args") or {}).items():
        if isinstance(v, str) and v[:1] in "\"{[":
            try:
                v = json.loads(v)
            except ValueError:
                pass
        out[k] = v
    return tc.get("name", ""), out


def real(p):
    return os.path.realpath(os.path.expanduser(p))


def under(path, roots):
    path = real(path)
    return any(path == real(r) or path.startswith(real(r).rstrip("/") + "/") for r in roots if r)


def latest_user(payload):
    path = payload.get("transcriptPath") or ""
    conv = payload.get("conversationId") or ""
    if not os.path.exists(path) and conv:
        path = os.path.join(HOME, ".gemini/antigravity-cli/brain", conv, ".system_generated/logs/transcript.jsonl")
    msg, step = "", -1
    try:
        with open(path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("source") == "USER_EXPLICIT" and rec.get("type") == "USER_INPUT":
                    m = re.search(r"<USER_REQUEST>\n?(.*?)\n?</USER_REQUEST>", rec.get("content", ""), re.S)
                    msg, step = (m.group(1) if m else rec.get("content", "")).strip(), rec.get("step_index", -1)
    except OSError:
        pass
    return msg, step


APPROVAL = re.compile(r"^\s*(y|yes|yeah|yep|yup|ok|okay|sure|approved?|go ahead|go for it|do it|proceed|confirm(ed)?|"
                      r"allow(ed)?|run it|continue)\b", re.I)


def approved(payload, action_text):
    msg, step = latest_user(payload)
    if not msg:
        return False
    norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
    if not ((APPROVAL.match(msg) and len(msg) < 300) or (action_text and norm(action_text) in norm(msg))):
        return False
    token = os.path.join(STATE, "approvals", f"{payload.get('conversationId', '')}-{step}")
    if os.path.exists(token):
        return False
    os.makedirs(os.path.dirname(token), exist_ok=True)
    open(token, "w").close()
    return True


def script_findings(cmd, cwd):
    found = []
    for m in list(INTERP.finditer(cmd)) + list(DIRECT_SCRIPT.finditer(cmd)):
        rel = m.group(6) if m.re is INTERP else m.group(2) + m.group(3)
        path = rel if os.path.isabs(os.path.expanduser(rel)) else os.path.join(cwd or os.getcwd(), rel)
        path = real(path)
        try:
            if os.path.getsize(path) > MAX_SCRIPT:
                found.append((path, "is too large to inspect", None))
                continue
            with open(path, errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        digest = hashlib.sha256(text.encode()).hexdigest()[:16]
        checks = NEVER + CONFIRM + SCRIPT_RX if path.endswith(SHELL_EXT) else NEVER + SCRIPT_RX
        for rx, why in checks:
            hit = re.search(rx, text, re.M)
            if hit:
                line = text.count("\n", 0, hit.start()) + 1
                found.append((path, f"{why} (line {line}: {text.splitlines()[line - 1].strip()[:80]})", digest))
                break
    return found


def classify(payload, name, a):
    roots = [r for r in (payload.get("workspacePaths") or [])]
    cwd = a.get("Cwd") if isinstance(a.get("Cwd"), str) else ""
    if cwd:
        roots.append(cwd)
    own_brain = os.path.join(HOME, ".gemini/antigravity-cli/brain", payload.get("conversationId", "") or "-")

    def off_task(p):
        return bool(OFF_TASK.search(real(p) + "/")) and not under(p, [own_brain])

    if name == "run_command":
        cmd = a.get("CommandLine") or ""
        for rx, why in NEVER:
            if re.search(rx, cmd):
                return "never", why, cmd
        for rx, why in CONFIRM:
            if re.search(rx, cmd, re.I if "DROP" in rx else 0):
                return "confirm", why, cmd
        if INLINE.search(cmd):
            for rx, why in SCRIPT_RX:
                if re.search(rx, cmd):
                    return "confirm", f"inline code that {why}", cmd
        if SECRET.search(cmd):
            return "confirm", "touches credentials, keys or environment secrets", cmd
        if CONTROL_RX.search(cmd):
            return "confirm", "touches the agent's own settings, hooks or plugins", cmd
        if OFF_TASK.search(cmd) and own_brain not in cmd:
            return "confirm", "reaches into another app's private data (off-task)", cmd
        for path, why, digest in script_findings(cmd, cwd):
            marker = os.path.join(STATE, "scripts", digest or "x")
            if digest and os.path.exists(marker):
                continue
            return "confirm", f"script {path} {why}", cmd + (f"\n#script:{digest}" if digest else "")
        return "allow", "", cmd

    if name == "view_file":
        p = str(a.get("AbsolutePath", ""))
        if SECRET.search(p):
            return "confirm", "reads a credentials/secret file", p
        if any(real(p) == c or real(p).startswith(c + "/") for c in CONTROL):
            return "confirm", "reads the agent's own settings, hooks or plugins (off-task)", p
        if off_task(p):
            return "confirm", "reads another app's private data (off-task)", p
        return "allow", "", p

    if name in ("write_to_file", "replace_file_content"):
        p = str(a.get("TargetFile", ""))
        rp = real(p)
        if any(rp == c or rp.startswith(c + "/") for c in CONTROL):
            return "confirm", "modifies the agent's own settings, hooks or plugins", p
        if SECRET.search(rp) or SENSITIVE_WRITE.search(rp):
            return "confirm", "writes a sensitive file (shell startup, git internals, keys or system dir)", p
        if off_task(rp):
            return "confirm", "writes into another app's private data (off-task)", p
        if not under(rp, roots + WRITE_OK_OUTSIDE):
            return "confirm", "writes outside the project folder", p
        return "allow", "", p

    if name == "read_url_content":
        u = str(a.get("Url", ""))
        if re.search(r"[?&](key|token|secret|password|passwd|auth|api[_-]?key|access_token|session)=", u, re.I):
            return "confirm", "URL carries a secret-looking parameter", u
        return "allow", "", u

    if name == "call_mcp_tool":
        server, tool = str(a.get("ServerName", "")), str(a.get("ToolName", ""))
        if server == "chrome-devtools":
            if tool in ("fill_form", "upload_file", "handle_dialog"):
                return "confirm", f"browser action {tool} may submit data", f"{server}/{tool}"
            return "allow", "", f"{server}/{tool}"
        return "confirm", f"unrecognised MCP tool {server}/{tool}", f"{server}/{tool}"

    if name == "schedule":
        return "confirm", "creates a scheduled/recurring job", json.dumps(a)[:200]

    return "allow", "", ""


def log(entry):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        os.makedirs(STATE, exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def fail_closed(raw, err):
    """Guard crashed or got bad input: let clearly read-only tools through, block everything else."""
    m = re.search(r'"name"\s*:\s*"([a-z_]+)"', raw or "")
    if m and m.group(1) in READ_ONLY_TOOLS:
        print('{"decision":"allow"}')
        return
    log({"decision": "guard-error", "why": err[:200], "raw": (raw or "")[:300]})
    print(json.dumps({"decision": "deny", "reason": "Blocked: the safety guard could not check this action "
                      f"({err[:80]}). Tell the user; do not try to work around it."}))


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get("toolCall"), dict):
            raise ValueError("malformed hook input")
        run(payload)
    except Exception as e:
        fail_closed(raw, f"{type(e).__name__}: {e}")


def run(payload):
    name, a = args_of(payload)
    verdict, why, action = classify(payload, name, a)
    base = {"tool": name, "action": action[:300], "conv": payload.get("conversationId", "")}

    if verdict == "allow":
        print('{"decision":"allow"}')
        return
    if verdict == "never":
        log({**base, "decision": "never", "why": why})
        reason = (f"Blocked permanently ({why}). This is never run by the agent. Tell the user; if they really want it, "
                  "they must run it themselves in their own terminal.")
        print(json.dumps({"decision": "deny", "reason": reason}))
        return
    cmd_only = action.split("\n#script:")[0]
    if approved(payload, cmd_only):
        if "\n#script:" in action:
            os.makedirs(os.path.join(STATE, "scripts"), exist_ok=True)
            open(os.path.join(STATE, "scripts", action.split("\n#script:")[1]), "w").close()
        log({**base, "decision": "approved", "why": why})
        print('{"decision":"allow"}')
        return
    log({**base, "decision": "blocked", "why": why})
    reason = (f"Blocked by strict mode: {why}. Ask the user for approval in plain text (not ask_question): state the "
              "exact command/action and what it will do, then end your turn and wait. Their reply 'yes' approves this "
              "one action; then retry it exactly. Do not achieve the same outcome another way (different command, "
              "script, tool, or splitting it up). Continue with other parts of the task that don't need it.")
    print(json.dumps({"decision": "deny", "reason": reason}))


if __name__ == "__main__":
    main()
