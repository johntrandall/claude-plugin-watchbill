"""watchbill configuration resolver (a module; `watchbill config` is its command line).

Every value the plugin's tools and hooks need comes from here, in this order:
  0. EVAL_WATCHBILL_<KEY>: the same, for `claude plugin eval` cases, which may set only EVAL_*
     variables; it lets a case pin its configuration or neutralise the operator's
  1. the environment variable WATCHBILL_<KEY> (upper case; a list is comma-separated)
  2. the hook environment variable CLAUDE_PLUGIN_OPTION_<KEY> (Claude Code exports each
     configured plugin option to hook processes under this name)
  3. the plugin's options in the user settings file, read only:
     {"pluginConfigs": {"watchbill@<marketplace>": {"options": {KEY: value}}}}
  4. the config file, read only: {KEY: value} (or {"options": {KEY: value}}), kept outside
     Claude Code's plugin store so a reinstall or a marketplace re-registration (which emptied
     pluginConfigs on 2026-10-15) cannot wipe it. `watchbill config --write-file` fills it from
     the resolved values.
  5. the default in this file.
Defaults are resolved here, never taken from the manifest: an option that was declared but
never configured does not reach hooks or skills.

The config file is $WATCHBILL_CONFIG_FILE, else $CLAUDE_CONFIG_DIR/watchbill.json, else
~/.claude/watchbill.json (inside the ~/.claude folder, so a user who keeps that folder in git
keeps the file with it).

The settings file is $WATCHBILL_SETTINGS_FILE, else $CLAUDE_CONFIG_DIR/settings.json, else
~/.claude/settings.json. With more than one watchbill@… entry, $WATCHBILL_PLUGIN_ID picks one,
else the one the user-scope install names (installed_plugins.json), else the first that is not
@inline.
"""
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # the plugin root

# key -> (type, default, description). Types: string, list, bool, number, path.
OPTIONS = {
    "human_name": ("string", "the human", "how seats name the human in the loop"),
    "forbidden_models": ("list", [], "models no seat or delegate may run on, per role: `haiku` for every role, "
                                  "`architect: none` or `steward: haiku opus` for one role (spawns are refused)"),
    "require_explicit_model": ("bool", True, "every Agent call and session start must name a model"),
    "alert_channels": ("string", "tab glyph only", "how a seat gets the human's attention, in order"),
    "decision_channels": ("string", "chat", "where the human gives decisions"),
    "drafting_tool": ("path", "obsidian-track-changes-agent", "the Track Changes tool: a command on PATH (the obsidian-track-changes-agent "
                                                "plugin provides `obsidian-track-changes-agent`) or a path to one with the same subcommands"),
    "drafting_author": ("string", None, "the human's author name in Track Changes (default: human_name)"),
    "headroom_command": ("string", "", "a load check run before every spawn; empty skips it"),
    "scheduler": ("string", "none", "what restarts seats on a schedule"),
    "infra_home": ("path", "", "where infrastructure faults go; empty sends them to the human"),
    "workspace_label": ("string", "{SUBJECT} system", "the label of a system's workspace"),
    "overlay_file": ("path", "", "a private markdown file of rules injected at session start"),
    "relief_deadline_minutes": ("number", 30, "how long each side of a relief waits for the other"),
    "handoff_offer_tokens": ("number", 400000, "context size at which a seat offers a handoff (cost band)"),
    "handoff_hard_percent": ("number", 85, "context percentage at which a seat hands off"),
    "context_window_tokens": ("number", 1000000, "the context window the percentage is taken of"),
}


def settings_file():
    if os.environ.get("WATCHBILL_SETTINGS_FILE"):
        return os.environ["WATCHBILL_SETTINGS_FILE"]
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(base, "settings.json")


def config_file():
    if os.environ.get("WATCHBILL_CONFIG_FILE"):
        return os.environ["WATCHBILL_CONFIG_FILE"]
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(base, "watchbill.json")


def file_options():
    """(path, options dict, exists) from the config file; unknown keys are kept for --explain."""
    path = config_file()
    data = _load_json(path)
    opts = data.get("options") if isinstance(data.get("options"), dict) else data
    return path, {k: v for k, v in opts.items() if not k.startswith("_")}, os.path.isfile(path)


def plugins_file():
    if os.environ.get("WATCHBILL_PLUGINS_FILE"):
        return os.environ["WATCHBILL_PLUGINS_FILE"]
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(base, "plugins", "installed_plugins.json")


def _load_json(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def plugin_options(settings=None):
    """(plugin id, options dict, why) from the settings file's pluginConfigs."""
    configs = (settings if settings is not None else _load_json(settings_file())).get("pluginConfigs") or {}
    ids = sorted(k for k in configs if k.split("@", 1)[0] == "watchbill")
    if not ids:
        return "", {}, "no watchbill@… entry in pluginConfigs"
    want = os.environ.get("WATCHBILL_PLUGIN_ID")
    pick, why = "", ""
    if want:
        pick, why = (want, "$WATCHBILL_PLUGIN_ID") if want in ids else ("", f"$WATCHBILL_PLUGIN_ID={want} not found")
    elif len(ids) == 1:
        pick, why = ids[0], "the only entry"
    else:
        installed = [k for k, v in (_load_json(plugins_file()).get("plugins") or {}).items()
                     if k in ids and any(e.get("scope") == "user" for e in (v if isinstance(v, list) else [v]))]
        if installed:
            pick, why = installed[0], "the user-scope install"
        else:
            pick = next((k for k in ids if not k.endswith("@inline")), ids[0])
            why = "first of " + ", ".join(ids)
    entry = configs.get(pick) or {}
    opts = entry.get("options") if isinstance(entry.get("options"), dict) else {}
    return pick, opts, why


def _coerce(kind, value):
    """A raw value (string from the environment, or JSON from settings) as the option's type."""
    if kind == "list":
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        return [v.strip() for v in str(value).split(",") if v.strip()]
    if kind == "bool":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")
    if kind == "number":
        try:
            n = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"not a number: {value!r}")
        return int(n) if n == int(n) else n
    if kind == "path":
        s = str(value).replace("${CLAUDE_PLUGIN_ROOT}", ROOT)
        return os.path.expanduser(s) if s else ""
    return str(value)


def _caches(_cache):
    """The per-call cache: {"plugin": plugin_options(), "file": file_options()}; a bare
    plugin_options() tuple (older callers) is accepted too."""
    if isinstance(_cache, dict):
        return _cache
    return {"plugin": _cache if _cache is not None else plugin_options(), "file": file_options()}


def resolve(key, _cache=None):
    """(value, source) for one option. Source: eval env, env, hook-env, settings <id>,
    file <path>, default."""
    if key not in OPTIONS:
        raise KeyError(f"unknown option {key!r}; known: {', '.join(OPTIONS)}")
    kind, default, _ = OPTIONS[key]
    for var, source in ((f"EVAL_WATCHBILL_{key.upper()}", "eval env"), (f"WATCHBILL_{key.upper()}", "env"),
                        (f"CLAUDE_PLUGIN_OPTION_{key.upper()}", "hook-env")):
        # (EVAL_)WATCHBILL_<KEY>="" is an explicit empty value; an empty plugin option is unset
        # (the install dialog writes "" for an option left blank)
        if var in os.environ and (source != "hook-env" or os.environ[var] != ""):
            try:
                return _coerce(kind, os.environ[var]), f"{source} {var}"
            except ValueError:
                pass  # a bad value falls through to the next source
    _cache = _caches(_cache)
    pid, opts, _ = _cache["plugin"]
    if key in opts and opts[key] not in (None, ""):
        try:
            return _coerce(kind, opts[key]), f"settings {pid}"
        except ValueError:
            pass
    fpath, fopts, _ = _cache["file"]
    if key in fopts and fopts[key] not in (None, ""):
        try:
            return _coerce(kind, fopts[key]), f"file {fpath}"
        except ValueError:
            pass
    if key == "drafting_author":
        name, src = resolve("human_name", _cache)
        return name, f"human_name ({src})"
    return (_coerce(kind, default) if default not in (None, "") or kind == "path" else default), "default"


def resolve_all():
    """{key: (value, source)} for every option, reading the settings and config files once."""
    cache = {"plugin": plugin_options(), "file": file_options()}
    return {k: resolve(k, cache) for k in OPTIONS}


def is_configured(values=None):
    """Does any value come from somewhere other than the defaults?"""
    v = values or resolve_all()
    return any(not src.startswith("default") and not src.startswith("human_name (default") for _, src in v.values())


def write_file(values=None, path=None):
    """Write every non-default resolved value into the config file (merged over what it holds,
    unknown keys kept), so the configuration survives a plugin reinstall. Returns (path, written)."""
    v = values or resolve_all()
    path = path or config_file()
    data = _load_json(path)
    existing = data.get("options") if isinstance(data.get("options"), dict) else data
    written = {k: val for k, (val, src) in v.items()
               if not src.startswith("default") and not src.startswith("human_name (")}
    merged = {**existing, **written}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(merged, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return path, written


def eval_pinned():
    """Does an eval case pin the configuration (any EVAL_WATCHBILL_* variable)? Such a session
    counts as inside a watchbill system for the hooks, since eval sandboxes have no owners file."""
    return any(k.startswith("EVAL_WATCHBILL_") for k in os.environ)


def get(key):
    return resolve(key)[0]


def role_name(role):
    """A role as the configuration names it: `watchbill:rules-lead`, `rules-lead` and `rules` are
    all `rules`. It is the role being launched (a seat kind, a watchbill agent type), never the
    caller; '' for a launch that names none."""
    r = (role or "").strip().strip("'\"").lower()
    if r.startswith("watchbill:"):
        r = r[len("watchbill:"):]
    if r.endswith("-lead"):
        r = r[:-len("-lead")]
    return r


ROLE_ENTRY = re.compile(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*)$")


def forbidden_models_for(role, forbidden=None):
    """The forbidden models for one role. An entry `<model>` forbids it for every role; an entry
    `<role>: <models>` (space-separated; `none` for nothing) is that role's whole list and
    replaces the every-role entries for it. A launch that names no role gets the every-role list."""
    entries = forbidden if forbidden is not None else get("forbidden_models")
    base, per_role = [], {}
    for e in entries:
        m = ROLE_ENTRY.match(str(e))
        if m:
            per_role[role_name(m[1])] = [x for x in m[2].replace("|", " ").split() if x.lower() != "none"]
        elif str(e).strip():
            base.append(str(e).strip())
    r = role_name(role)
    return per_role[r] if r in per_role else base


def is_forbidden_model(model, forbidden=None, role=""):
    """Does this model name or id name a model forbidden for this role? 'opus' matches opus, Opus,
    claude-opus-5-5 and opus[1m]; matching is on the whole name, never on quoted text."""
    m = (model or "").strip().strip("'\"").lower()
    if not m:
        return ""
    for f in forbidden_models_for(role, forbidden):
        f = f.strip().lower()
        if not f:
            continue
        base = m.split("[", 1)[0]
        if base == f or base == f"claude-{f}" or base.startswith(f"claude-{f}-") or base.startswith(f"{f}-"):
            return f
    return ""


def drafting_tool_file(tool=None):
    """The Track Changes tool as a file: the configured drafting_tool when it is a path to one,
    else that command found on PATH; '' when neither exists. The obsidian-track-changes-agent plugin provides
    the command (`obsidian-track-changes-agent`; `obsidian-track-changes-agent install-links` puts it on PATH)."""
    tool = get("drafting_tool") if tool is None else tool
    if not tool:
        return ""
    if os.path.sep in tool:
        return tool if os.path.isfile(tool) else ""
    return shutil.which(tool) or ""


def overlay_text(limit=12000):
    """(path, text) of the overlay file, text cut at `limit` characters; ('', '') when unset."""
    path = get("overlay_file")
    if not path:
        return "", ""
    try:
        with open(path, errors="replace") as f:
            text = f.read()
    except OSError as e:
        return path, f"(overlay file not readable: {e})"
    return path, text if len(text) <= limit else text[:limit] + "\n… (overlay cut at %d characters)" % limit


def summary_lines(values=None):
    """The resolved values as the short lines the session-start context shows."""
    values = values or resolve_all()
    v = {k: val for k, (val, _) in values.items()}
    forbidden = "; ".join(v["forbidden_models"]) or "none"
    lines = [
        f"The human in the loop: {v['human_name']} (Track Changes author: {v['drafting_author']}).",
        f"Forbidden models: {forbidden}." + (" Every Agent call and session start names its model."
                                             if v["require_explicit_model"] else ""),
        f"Alerts: {v['alert_channels']}. Decisions arrive by: {v['decision_channels']}.",
        f"Scheduler: {v['scheduler']}. Infrastructure faults go to: {v['infra_home'] or v['human_name']}.",
        f"Track Changes tool: {v['drafting_tool']}"
        + (f" ({found})." if (found := drafting_tool_file(v['drafting_tool'])) else
           " (not found: install the obsidian-track-changes-agent plugin and run `obsidian-track-changes-agent install-links`)."),
        f"Handoff: offer one at {v['handoff_offer_tokens']:,} tokens of context (cost band); hand off at "
        f"{v['handoff_hard_percent']} % of {v['context_window_tokens']:,}. Check with `watchbill context`.",
        f"Relief deadline: {v['relief_deadline_minutes']} minutes on each side (`herdr-lifecycle relief-check`).",
    ]
    if v["headroom_command"]:
        lines.append(f"Load check before every spawn: `{v['headroom_command']}`.")
    if not is_configured(values):
        lines.append(f"No configuration found (no watchbill@… entry in pluginConfigs, no {config_file()}): "
                     f"every value above is a default. `watchbill config --write-file` keeps a copy that "
                     f"survives a plugin reinstall.")
    return lines
