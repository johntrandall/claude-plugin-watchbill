"""watchbill configuration resolver (a module; `watchbill config` is its command line).

Every value the plugin's tools and hooks need comes from here, in this order:
  0. EVAL_WATCHBILL_<KEY>: the same, for `claude plugin eval` cases, which may set only EVAL_*
     variables; it lets a case pin its configuration or neutralise the operator's
  1. the environment variable WATCHBILL_<KEY> (upper case; a list is comma-separated)
  2. the hook environment variable CLAUDE_PLUGIN_OPTION_<KEY> (Claude Code exports each
     configured plugin option to hook processes under this name)
  3. the plugin's options in the user settings file, read only:
     {"pluginConfigs": {"watchbill@<marketplace>": {"options": {KEY: value}}}}
  4. the default in this file.
Defaults are resolved here, never taken from the manifest: an option that was declared but
never configured does not reach hooks or skills.

The settings file is $WATCHBILL_SETTINGS_FILE, else $CLAUDE_CONFIG_DIR/settings.json, else
~/.claude/settings.json. With more than one watchbill@… entry, $WATCHBILL_PLUGIN_ID picks one,
else the one the user-scope install names (installed_plugins.json), else the first that is not
@inline.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # the plugin root

# key -> (type, default, description). Types: string, list, bool, number, path.
OPTIONS = {
    "human_name": ("string", "the human", "how seats name the human in the loop"),
    "forbidden_models": ("list", [], "models no seat or delegate may run on (spawns are refused)"),
    "require_explicit_model": ("bool", True, "every Agent call and session start must name a model"),
    "alert_channels": ("string", "tab glyph only", "how a seat gets the human's attention, in order"),
    "decision_channels": ("string", "chat", "where the human gives decisions"),
    "drafting_tool": ("path", "${CLAUDE_PLUGIN_ROOT}/bin/criticmarkup.py", "the Track Changes tool"),
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


def resolve(key, _cache=None):
    """(value, source) for one option. Source: eval env, env, hook-env, settings <id>, default."""
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
    pid, opts, _ = _cache if _cache is not None else plugin_options()
    if key in opts and opts[key] not in (None, ""):
        try:
            return _coerce(kind, opts[key]), f"settings {pid}"
        except ValueError:
            pass
    if key == "drafting_author":
        name, src = resolve("human_name", _cache)
        return name, f"human_name ({src})"
    return (_coerce(kind, default) if default not in (None, "") or kind == "path" else default), "default"


def resolve_all():
    """{key: (value, source)} for every option, reading the settings file once."""
    cache = plugin_options()
    return {k: resolve(k, cache) for k in OPTIONS}


def eval_pinned():
    """Does an eval case pin the configuration (any EVAL_WATCHBILL_* variable)? Such a session
    counts as inside a watchbill system for the hooks, since eval sandboxes have no owners file."""
    return any(k.startswith("EVAL_WATCHBILL_") for k in os.environ)


def get(key):
    return resolve(key)[0]


def is_forbidden_model(model, forbidden=None):
    """Does this model name or id name a forbidden model? 'opus' matches opus, Opus,
    claude-opus-5-5 and opus[1m]; matching is on the whole name, never on quoted text."""
    m = (model or "").strip().strip("'\"").lower()
    if not m:
        return ""
    for f in (forbidden if forbidden is not None else get("forbidden_models")):
        f = f.strip().lower()
        if not f:
            continue
        base = m.split("[", 1)[0]
        if base == f or base == f"claude-{f}" or base.startswith(f"claude-{f}-") or base.startswith(f"{f}-"):
            return f
    return ""


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
    v = {k: val for k, (val, _) in (values or resolve_all()).items()}
    forbidden = ", ".join(v["forbidden_models"]) or "none"
    lines = [
        f"The human in the loop: {v['human_name']} (Track Changes author: {v['drafting_author']}).",
        f"Forbidden models: {forbidden}." + (" Every Agent call and session start names its model."
                                             if v["require_explicit_model"] else ""),
        f"Alerts: {v['alert_channels']}. Decisions arrive by: {v['decision_channels']}.",
        f"Scheduler: {v['scheduler']}. Infrastructure faults go to: {v['infra_home'] or v['human_name']}.",
        f"Track Changes tool: {v['drafting_tool']}.",
        f"Handoff: offer one at {v['handoff_offer_tokens']:,} tokens of context (cost band); hand off at "
        f"{v['handoff_hard_percent']} % of {v['context_window_tokens']:,}. Check with `watchbill context`.",
        f"Relief deadline: {v['relief_deadline_minutes']} minutes on each side (`herdr-lifecycle relief-check`).",
    ]
    if v["headroom_command"]:
        lines.append(f"Load check before every spawn: `{v['headroom_command']}`.")
    return lines
