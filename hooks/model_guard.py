#!/usr/bin/env python3
"""watchbill model guard: forbidden models hold by construction, and every start names a model.

PreToolUse hook for Agent (and its older name Task) and Bash. Configuration (watchbill
config): forbidden_models (empty by default: nothing is forbidden; an entry `<role>: <models>`
is one role's own list, so `haiku, architect: none` forbids haiku for everyone but the
architect) and require_explicit_model (default true). The role checked is the one being
launched: an Agent call's watchbill subagent_type, a `claude --agent watchbill:<role>`, a
`spawn --seat <kind>`; anything else gets the every-role list. Inside a watchbill system (a repository with
dev-docs/owners.yaml) or in a watchbill plugin agent:

  Agent    DENIES a call whose model is forbidden; with require_explicit_model, reminds
           the model to pass a model when a call names none and its type is not a
           watchbill agent (those pin their own).
  Bash     reads the command as the shell would (quoted text and heredoc bodies are
           arguments, never commands) and DENIES
             - `claude` that starts a session with a forbidden --model; with no --model
               and no ANTHROPIC_MODEL, the settings default model decides, so the start
               is denied when require_explicit_model is set (nothing pins that default)
               or when the settings default is forbidden (`claude -p …` included);
             - an assignment ANTHROPIC_MODEL=<forbidden> (prefix or export);
             - `herdr-lifecycle spawn` with a forbidden --model, and (with
               require_explicit_model) a plain `spawn <name>` (not --seat) whose claude
               arguments after `--` name no --model.
           `claude plugin|mcp|config|doctor|update|install|auth …`, `--version` and
           `--help` start no session and pass.

Everywhere else it is silent, so the human's own sessions and other projects are
untouched.
"""
import json
import os
import re
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "bin"))
import watchbill_config as config  # noqa: E402

FLAG_MODEL = re.compile(r"--model(?:=|\s+)['\"]?([\w.\[\]-]+)", re.IGNORECASE)
LAUNCHER = re.compile(r"(?:^|[\s;&|(])(?:claude|herdr-lifecycle\s+spawn)\b")
MODEL_ENV = "ANTHROPIC_MODEL"
NO_SESSION = {"plugin", "plugins", "mcp", "config", "doctor", "update", "upgrade", "install",
              "migrate-installer", "setup-token", "auth", "login", "logout"}
INFO_FLAGS = {"--version", "-v", "--help", "-h"}
WRAPPERS = {"env", "exec", "nohup", "time", "command", "caffeinate"}
OPERATORS = {";", "&", "&&", "|", "||", "(", ")", "\n", ";;", "|&"}
HEREDOC = re.compile(r"(<<-?[ \t]*(['\"]?)(\w+)\2)([^\n]*)\n.*?\n[ \t]*\3[ \t]*(?=\n|$)", re.DOTALL)
ASSIGN = re.compile(r"^([A-Za-z_]\w*)=(.*)$", re.DOTALL)

NO_MODEL = ("watchbill: this starts a Claude session with no model, so it gets the settings default, "
            "which nothing pins. Pass --model with an allowed model.")


_settings = {}


def setting(key):
    """A configuration value, resolved once per hook run."""
    if key not in _settings:
        _settings[key] = config.get(key)
    return _settings[key]


def forbidden(model, role=""):
    """The forbidden model this name matches for the launched role, or ''."""
    return config.is_forbidden_model(model, setting("forbidden_models"), role)


def never(model, role=""):
    where = f"for role {role}" if role else "here"
    return (f"watchbill: {model} is a forbidden model {where} in this configuration (forbidden_models: "
            f"{'; '.join(setting('forbidden_models'))}). Pick another model.")


def settings_default_model():
    """The `model` key of the user settings file (the default a session without --model gets)."""
    try:
        with open(config.settings_file()) as f:
            return str(json.load(f).get("model") or "")
    except (OSError, ValueError, AttributeError):
        return ""



def in_watchbill_system(cwd, agent_type):
    if (agent_type and agent_type.startswith("watchbill:")) or config.eval_pinned():
        return True
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and os.path.isfile(os.path.join(out.stdout.strip(), "dev-docs", "owners.yaml"))


def respond(decision=None, reason="", context=""):
    specific = {"hookEventName": "PreToolUse"}
    if decision:
        specific["permissionDecision"] = decision
        specific["permissionDecisionReason"] = reason
    if context:
        specific["additionalContext"] = context
    print(json.dumps({"hookSpecificOutput": specific}))


def commands(command):
    """The shell command as a list of simple commands (lists of words). Quoted strings stay one
    word and heredoc bodies are dropped, so text that only mentions a launcher never matches."""
    command = HEREDOC.sub(lambda m: m.group(1) + m.group(4), command)
    lex = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    out, cur = [], []
    for token in lex:
        if token in OPERATORS:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(token)
    if cur:
        out.append(cur)
    return out


def flag_value(args, flag):
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(flag + "="):
            return a[len(flag) + 1:]
    return None


def bash_verdict(command):
    """A deny reason for this shell command, or ''."""
    try:
        cmds = commands(command)
    except ValueError:  # unbalanced quotes: fall back to the plain flag check
        if LAUNCHER.search(command):
            hit = next((forbidden(m) for m in FLAG_MODEL.findall(command) if forbidden(m)), "")
            return never(hit) if hit else ""
        return ""
    exported = {}
    for words in cmds:
        env, i = {}, 0
        if words and words[0] == "export":
            for w in words[1:]:
                m = ASSIGN.match(w)
                if m:
                    exported[m[1]] = m[2]
                    if m[1] == MODEL_ENV and forbidden(m[2]):
                        return never(forbidden(m[2]))
            continue
        while i < len(words):  # VAR=value prefixes and wrappers before the command word
            m = ASSIGN.match(words[i])
            if m:
                env[m[1]] = m[2]
                i += 1
            elif os.path.basename(words[i]) in WRAPPERS or (env and words[i].startswith("-")):
                i += 1
            else:
                break
        if i >= len(words):
            if forbidden(env.get(MODEL_ENV, "")):
                return never(forbidden(env[MODEL_ENV]))
            continue
        word, args = os.path.basename(words[i]), words[i + 1:]
        env_model = env.get(MODEL_ENV) or exported.get(MODEL_ENV) or ""
        claude_args = args[args.index("--") + 1:] if "--" in args else []
        role = ""  # the launched role: --agent watchbill:<role>, or spawn --seat <kind>
        if word == "claude":
            role = config.role_name(flag_value(args, "--agent") or "")
        elif word == "herdr-lifecycle" and args[:1] == ["spawn"]:
            role = config.role_name(flag_value(args, "--seat") or flag_value(claude_args, "--agent") or "")
        if forbidden(env.get(MODEL_ENV, ""), role):
            return never(forbidden(env[MODEL_ENV], role), role)
        if word == "claude":
            positional = [a for a in args if not a.startswith("-")]
            if INFO_FLAGS & set(args) or (positional and positional[0] in NO_SESSION
                                          and args.index(positional[0]) == 0):
                continue
            model = flag_value(args, "--model")
            if model and forbidden(model, role):
                return never(forbidden(model, role), role)
            if not model and env_model and forbidden(env_model, role):
                return never(forbidden(env_model, role), role)
            if not model and not env_model:
                if setting("require_explicit_model"):
                    return NO_MODEL
                default = settings_default_model()
                if forbidden(default, role):
                    return (f"watchbill: this starts a Claude session with no model, so it gets the settings "
                            f"default {default}, a forbidden model. Pass --model with an allowed model.")
        elif word == "herdr-lifecycle" and args[:1] == ["spawn"]:
            model = flag_value(args, "--model")
            if model and forbidden(model, role):
                return never(forbidden(model, role), role)
            claude_model = flag_value(claude_args, "--model")
            if claude_model and forbidden(claude_model, role):
                return never(forbidden(claude_model, role), role)
            if "--seat" not in args and setting("require_explicit_model"):  # spawn --seat requires --model itself
                if not flag_value(claude_args, "--model"):
                    return ("watchbill: a plain `herdr-lifecycle spawn <name>` passes no model unless you give "
                            "one after `--` (`-- --model opus`); without it the session gets the settings.json "
                            "default. Add it, or use `spawn --seat`.")
    return ""


def main():
    try:
        hook_input = json.load(sys.stdin)
    except ValueError:
        return 0
    tool = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input") or {}
    if not in_watchbill_system(hook_input.get("cwd") or os.getcwd(), hook_input.get("agent_type") or ""):
        return 0
    if tool in ("Agent", "Task"):
        model = str(tool_input.get("model") or "")
        kind = str(tool_input.get("subagent_type") or "")
        role = config.role_name(kind) if kind.startswith("watchbill:") else ""
        if forbidden(model, role):
            respond("deny", never(forbidden(model, role), role) + " Or use a watchbill crew type, which pins its own model.")
        elif not model and not kind.startswith("watchbill:") and setting("require_explicit_model"):
            respond(context="watchbill: this Agent call names no model, so it gets whatever the session or "
                            "settings default is, which nothing pins. Pass model explicitly, or use a watchbill "
                            "crew type (watchbill:worker, reader, verifier, backfill, checker, escalation).")
    elif tool == "Bash":
        reason = bash_verdict(str(tool_input.get("command") or ""))
        if reason:
            respond("deny", reason)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
