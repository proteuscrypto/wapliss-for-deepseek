#!/usr/bin/env python3
"""Validate the Wapliss bundle for DeepSeek Harness (dsh).

Static checks follow the dsh bundle rules (docs/user/develop/basic/publish.md and the
cordis-plugin-development skill: references/host-plugin.md, references/mcp-bundle.md).

  python3 scripts/validate.py            # static checks
  python3 scripts/validate.py --live     # + checks against https://wapliss.com/mcp/v1
  WAPLISS_API_KEY=wp_live_... python3 scripts/validate.py --live   # + authenticated tools/list

Requires PyYAML (pip install pyyaml).
"""
import json, os, pathlib, re, struct, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL, WARN = [], []
EXPECTED_TOOLS = {
    "send_text_message", "send_image", "send_document", "send_audio", "send_video", "send_location",
    "send_contact", "send_poll", "forward_messages", "get_chats", "get_chat_history", "get_message",
    "get_last_incoming_messages", "get_last_outgoing_messages", "get_group", "get_account_status",
}


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond or not extra else f"  -> {extra}"))
    if not cond:
        FAIL.append(name)


def warn(name):
    print("WARN " + name)
    WARN.append(name)


def load_yaml(path):
    import yaml

    class Loader(yaml.SafeLoader):
        pass

    def js(loader, node):
        return {"!!js": loader.construct_scalar(node)}

    Loader.add_constructor("tag:yaml.org,2002:js", js)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)


def static():
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    check("package.json name", bool(re.fullmatch(r"(@[a-z0-9-]+/)?[a-z0-9][a-z0-9._-]*", pkg.get("name", ""))), pkg.get("name"))
    check("package.json semver version", bool(re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?", pkg.get("version", ""))))
    check("package.json description", len(pkg.get("description", "")) >= 40)
    check("package.json license MIT + LICENSE file", pkg.get("license") == "MIT" and (ROOT / "LICENSE").is_file())
    check("keywords include dsh-plugin", "dsh-plugin" in pkg.get("keywords", []))
    check("engines.dsh range declared", bool(pkg.get("engines", {}).get("dsh")))
    patch_rel = pkg.get("dsh", {}).get("bundle", {}).get("patch")
    check("dsh.bundle.patch declared", isinstance(patch_rel, str) and patch_rel)
    check("no dsh.plugin.json (metadata lives in package.json)", not (ROOT / "dsh.plugin.json").exists())
    check("no install/build scripts (config-only bundle)", not set(pkg.get("scripts", {})) & {"prepare", "install", "postinstall", "preinstall"})
    exports = pkg.get("exports", {})
    check("exports ./locale/*.json", exports.get("./locale/*.json") == "./locale/*.json")
    check("exports ./icon", "./icon" in exports)
    files = pkg.get("files", [])
    for f in ("cordis.patch.yml", "locale/*.json"):
        check(f"files includes {f}", f in files)

    # Icon: SVG/PNG/JPEG/WebP, <= 256 KiB, inside the package, valid bytes
    icon_rel = pkg.get("icon") or exports.get("./icon")
    icon = (ROOT / icon_rel).resolve() if icon_rel else None
    check("icon inside package", bool(icon) and ROOT in icon.parents and not icon.is_symlink(), icon_rel)
    if icon and icon.is_file():
        data = icon.read_bytes()
        check("icon <= 256 KiB", len(data) <= 256 * 1024, len(data))
        is_png = data[:8] == b"\x89PNG\r\n\x1a\n"
        check("icon is a valid PNG", is_png)
        if is_png:
            w, h = struct.unpack(">II", data[16:24])
            check("icon square >= 128px", w == h and w >= 128, f"{w}x{h}")
        check("icon listed in files", icon.name in files)

    # Locales: meta.title + meta.description, English required
    locales = sorted((ROOT / "locale").glob("*.json"))
    check("locale/en.json present", (ROOT / "locale" / "en.json").is_file())
    for loc in locales:
        meta = json.loads(loc.read_text(encoding="utf-8")).get("meta", {})
        check(f"locale {loc.stem}: meta.title + meta.description", bool(meta.get("title")) and len(meta.get("description", "")) >= 30)

    # Patch: one insert row for the in-box MCP client
    patch_path = ROOT / patch_rel
    check("patch file exists", patch_path.is_file())
    raw = patch_path.read_text(encoding="utf-8")
    check("no secrets committed in the patch", not re.search(r"wp_live_[0-9a-f]{8,}|wpl_at_|sk-[A-Za-z0-9]{16,}", raw))
    doc = load_yaml(patch_path)
    check("patch is a YAML list", isinstance(doc, list) and doc)
    rows = [r for op in doc for r in (op.get("insert") or [])] if isinstance(doc, list) else []
    check("exactly one inserted row", len(rows) == 1, rows)
    row = rows[0] if rows else {}
    cfg = row.get("config", {})
    check("row id is wapliss-whatsapp", row.get("id") == "wapliss-whatsapp")
    check("row uses @deepseek-ai/dsh-mcp-client", row.get("name") == "@deepseek-ai/dsh-mcp-client")
    check("serverName wapliss matches [A-Za-z0-9_-]{1,32}", cfg.get("serverName") == "wapliss")
    check("transport streamable-http", cfg.get("transport") == "streamable-http")
    check("url is https://wapliss.com/mcp/v1", cfg.get("url") == "https://wapliss.com/mcp/v1")
    auth = (cfg.get("headers") or {}).get("Authorization")
    check("Authorization header from WAPLISS_API_KEY", isinstance(auth, dict) and "process.env.WAPLISS_API_KEY" in auth.get("!!js", ""))
    disabled = row.get("disabled")
    check("row disabled when WAPLISS_API_KEY is missing", isinstance(disabled, dict) and "!process.env.WAPLISS_API_KEY" in disabled.get("!!js", ""))
    check("failOnStartupError false (harness still boots)", cfg.get("failOnStartupError") is False)
    allowed = {"serverName", "transport", "url", "headers", "toolCallTimeoutMs", "failOnStartupError", "maxInstructionBytes", "reconnect"}
    check("config keys accepted by dsh-mcp-client 0.2.x", set(cfg) <= allowed, set(cfg) - allowed)

    # Skill (dsh-skill-filesystem format)
    skill = ROOT / "skills" / "wapliss-whatsapp" / "SKILL.md"
    check("skills/wapliss-whatsapp/SKILL.md exists", skill.is_file())
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        import yaml
        fm = yaml.safe_load(m.group(1)) if m else {}
        check("skill name is kebab-case and matches folder", fm.get("name") == "wapliss-whatsapp")
        check("skill description present", len(fm.get("description", "")) >= 40)
        for flag in ("disable-model-invocation", "user-invocable"):
            if flag in fm:
                check(f"skill {flag} is boolean", isinstance(fm[flag], bool))
        check("skill uses dsh tool names mcp__wapliss__*", "mcp__wapliss__" in text)
        missing = [t for t in EXPECTED_TOOLS if f"`{t}`" not in text]
        check("skill documents all 16 tools", not missing, missing)
        check("skill never asks for the key in chat", "Never ask the user to paste the key" in text)

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    check("README has install command", "dsh plugin --profile" in readme and "github:proteuscrypto/wapliss-for-deepseek" in readme)
    check("README mentions WAPLISS_API_KEY", "WAPLISS_API_KEY" in readme)


def rpc(url, method, headers=None, rid=1):
    body = json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": {
        "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}}}).encode()
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
         "MCP-Protocol-Version": "2026-07-28", "User-Agent": "wapliss-dsh-validate/1.0"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}"), dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), dict(e.headers)
        except Exception:
            return e.code, raw[:200], dict(e.headers)


def live():
    url = "https://wapliss.com/mcp/v1"
    s, r, h = rpc(url, "server/discover")
    www = h.get("WWW-Authenticate") or h.get("www-authenticate") or ""
    check("live: unauthenticated -> 401", s == 401, s)
    check("live: WWW-Authenticate resource_metadata", "resource_metadata=" in www, www)
    s, r, _ = rpc(url, "tools/list", {"Authorization": "Bearer wp_live_" + "0" * 48})
    check("live: invalid API key -> 401", s == 401, s)
    key = os.environ.get("WAPLISS_API_KEY", "")
    if not key:
        warn("live: WAPLISS_API_KEY not set, authenticated checks skipped")
        return
    auth = {"Authorization": f"Bearer {key}"}
    s, r, _ = rpc(url, "server/discover", auth)
    check("live: server/discover with API key", s == 200 and "result" in r, r)
    s, r, _ = rpc(url, "tools/list", auth, 2)
    res = r.get("result", {}) if isinstance(r, dict) else {}
    names = {t.get("name") for t in res.get("tools", [])}
    check("live: tools/list returns the 16 tools", names == EXPECTED_TOOLS, names ^ EXPECTED_TOOLS)
    check("live: 2026-07-28 cacheable fields (ttlMs, cacheScope)", isinstance(res.get("ttlMs"), int) and res.get("cacheScope") in ("public", "private"), res.keys())


if __name__ == "__main__":
    static()
    if "--live" in sys.argv:
        live()
    print(f"\nRESULT: {'ALL PASS' if not FAIL else f'{len(FAIL)} FAILED'}" + (f" ({len(WARN)} warnings)" if WARN else ""))
    sys.exit(1 if FAIL else 0)
