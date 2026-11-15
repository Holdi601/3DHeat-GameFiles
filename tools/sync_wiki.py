"""Rebuild docs/wiki/ (the GitHub wiki's copy) from docs/*.md, so the wiki never says
something the Pages site does not. Run after editing docs/; never edit docs/wiki/ by hand.

    python tools/sync_wiki.py

index.md becomes Home.md; front matter is dropped; `page.md` links lose `.md`;
pictures point at the files in this repository; _Sidebar.md follows the site's menu."""
import os
import re
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
WIKI = os.path.join(DOCS, "wiki")


def repo_name():
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout
    return url.strip().rstrip("/").removesuffix(".git").split("/")[-1]


def front(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    return meta, text[m.end():].lstrip("\n")


def main():
    raw = f"https://raw.githubusercontent.com/Holdi601/{repo_name()}/main/docs/"
    pages = {}
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(DOCS, name), encoding="utf-8") as f:
            meta, body = front(f.read())
        stem = "Home" if name == "index.md" else name[:-3]
        body = re.sub(r"\]\(index\.md(#[^)]*)?\)", lambda m: "](Home" + (m.group(1) or "") + ")", body)
        body = re.sub(r"\]\(([\w.-]+)\.md(#[^)]*)?\)", lambda m: f"]({m.group(1)}{m.group(2) or ''})", body)
        body = re.sub(r"\]\((assets/[^)]+)\)", lambda m: f"]({raw}{m.group(1)})", body)
        pages[stem] = (meta, body)
    os.makedirs(WIKI, exist_ok=True)
    keep = {"_Sidebar.md"} | {s + ".md" for s in pages}
    for old in os.listdir(WIKI):
        if old.endswith(".md") and old not in keep:
            os.remove(os.path.join(WIKI, old))
    for stem, (meta, body) in pages.items():
        with open(os.path.join(WIKI, stem + ".md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    # The menu: top-level pages by nav_order, children under their parent's title.
    def order(item):
        return (int(item[1][0].get("nav_order", 999)), item[1][0].get("title", item[0]))
    top = [(s, p) for s, p in pages.items() if "parent" not in p[0]]
    lines = [f"**{_site_title()}**", ""]
    for stem, (meta, _) in sorted(top, key=order):
        lines.append(f"- [{meta.get('title', stem)}]({stem})")
        kids = [(s, p) for s, p in pages.items() if p[0].get("parent") == meta.get("title")]
        for kstem, (kmeta, _) in sorted(kids, key=order):
            lines.append(f"  - [{kmeta.get('title', kstem)}]({kstem})")
    with open(os.path.join(WIKI, "_Sidebar.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wiki: wrote", len(pages), "pages")


def _site_title():
    with open(os.path.join(DOCS, "_config.yml"), encoding="utf-8") as f:
        m = re.search(r"^title:\s*(.*)$", f.read(), re.M)
    return m.group(1).strip() if m else "Documentation"


if __name__ == "__main__":
    main()
