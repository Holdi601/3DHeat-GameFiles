"""Generate docs/cli-reference.md from the tool's own --help, so the option list cannot drift.
Run it after changing an option; `--check` is part of the release checklist (docs/maintaining.md).
usage: python tools/gen_docs_reference.py [--check]
--check exits 1 when the committed page differs from what the code prints (use before a release)."""
import os, re, subprocess, sys
CMD = [sys.executable, "-m", "heat3d_gamefiles"]
SHOWN = "python -m heat3d_gamefiles"
TITLE = "Command reference"
NAV = 3
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "cli-reference.md")

def run(args):
    env = dict(os.environ, HEAT3D_NO_UPDATE="1", COLUMNS="88", PYTHONIOENCODING="utf-8")
    r = subprocess.run(CMD + args, capture_output=True, text=True, env=env, encoding="utf-8")
    return (r.stdout or r.stderr).rstrip()

def verbs(top):
    m = re.search(r"\{([a-z0-9_,-]+)\}", top)
    return m.group(1).split(",") if m else []

def build():
    top = run(["--help"])
    name = SHOWN
    out = ["---", f"title: {TITLE}", f"nav_order: {NAV}", "---", "", f"# {TITLE}", "",
           "This page is generated from the program's own `--help` by `tools/gen_docs_reference.py`;",
           "do not edit it by hand. The other pages explain each command step by step.", "",
           f"## `{name}`", "", "```text", top, "```", ""]
    for v in verbs(top):
        out += [f"## `{v}`", "", "```text", run([v, "--help"]), "```", ""]
    return "\n".join(out)

if __name__ == "__main__":
    text = build()
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        sys.exit(0 if cur == text else 1)
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    print("wrote", os.path.normpath(OUT))
