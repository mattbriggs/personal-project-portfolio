"""
MkDocs hook — prepare_guide.py

At build time this hook:
  1. Copies DITA-generated Markdown from guide/out/markdown/ into
     site/src/guide/, stripping DITA heading attributes ({#id .class}).
  2. Replaces every  ![alt](images/foo.png)  reference with an inline
     Mermaid fenced code block sourced from guide/images/foo.mmd, so
     diagrams render natively via the MkDocs superfences + Mermaid CDN
     already configured in mkdocs.yml.
  3. Injects a Guide section into the MkDocs nav, derived from the DITA
     index.md table of contents.

Registered in mkdocs.yml:
  hooks:
    - tools/prepare_guide.py
"""

import logging
import re
import shutil
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.prepare_guide")

# All paths are relative to the project root (where mkdocs.yml lives).
GUIDE_SRC  = Path("guide/out/markdown")   # DITA markdown output
IMAGES_SRC = Path("guide/images")         # Mermaid .mmd sources
GUIDE_DEST = Path("site/src/guide")       # destination for MkDocs

# Matches DITA heading attribute blocks:  {#some-id .some-class}
_DITA_ATTR = re.compile(r"\s*\{#[\w-]+(?:\s+\.[\w-]+)*\}")

# Matches a Markdown image reference:  ![alt text](images/foo.png)
_IMAGE_REF = re.compile(r"!\[([^\]]*)\]\(images/([\w-]+)\.png\)")

# Matches a Markdown inline link:  [Link text](filename.md)
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")


# ---------------------------------------------------------------------------
# Mermaid source loading
# ---------------------------------------------------------------------------

def _load_mmd_map() -> dict[str, str]:
    """
    Return a dict mapping diagram stem → Mermaid source text.
    E.g. {"milestone-lifecycle": "stateDiagram-v2\n  ..."}
    """
    if not IMAGES_SRC.is_dir():
        return {}
    return {
        mmd.stem: mmd.read_text(encoding="utf-8").strip()
        for mmd in IMAGES_SRC.glob("*.mmd")
    }


# ---------------------------------------------------------------------------
# Markdown processing
# ---------------------------------------------------------------------------

def _make_mermaid_block(alt: str, source: str) -> str:
    """Wrap Mermaid source in a fenced code block, using alt text as a caption."""
    lines = [f"```mermaid", source, "```"]
    if alt:
        lines.append(f"*{alt}*")
    return "\n".join(lines)


def _scrub(text: str, mmd_map: dict[str, str]) -> str:
    """
    Process a single Markdown file:
      - Remove DITA {#id .class} attributes from heading lines.
      - Replace ![alt](images/foo.png) with an inline Mermaid code block
        when a matching foo.mmd exists; leave the reference unchanged otherwise.
    """
    def _replace_image(m: re.Match) -> str:
        alt, stem = m.group(1), m.group(2)
        if stem in mmd_map:
            return _make_mermaid_block(alt, mmd_map[stem])
        log.warning("Guide: no .mmd source for images/%s.png — leaving as-is", stem)
        return m.group(0)

    out = []
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("#"):
            line = _DITA_ATTR.sub("", line)
        # Image substitution operates on full lines (images are block-level in DITA output).
        line = _IMAGE_REF.sub(_replace_image, line)
        out.append(line)
    return "".join(out)


def _copy_and_scrub(mmd_map: dict[str, str]) -> None:
    """Recreate GUIDE_DEST, copying and scrubbing all .md files from GUIDE_SRC."""
    if GUIDE_DEST.exists():
        shutil.rmtree(GUIDE_DEST)
    GUIDE_DEST.mkdir(parents=True)

    md_count = 0
    for src_file in sorted(GUIDE_SRC.glob("*.md")):
        text = src_file.read_text(encoding="utf-8")
        (GUIDE_DEST / src_file.name).write_text(_scrub(text, mmd_map), encoding="utf-8")
        md_count += 1

    log.info("Guide: %d Markdown files copied to %s", md_count, GUIDE_DEST)


# ---------------------------------------------------------------------------
# Nav parsing
# ---------------------------------------------------------------------------

def _unescape(title: str) -> str:
    """Replace Markdown-escaped parentheses with literal parens."""
    return title.replace(r"\(", "(").replace(r"\)", ")")


def _parse_nav(index_path: Path) -> list:
    """
    Parse the DITA-generated index.md into a MkDocs nav list.

    The index uses a two-level nested list:
      - Section Name               ← plain text (no link) → nav section
          - [Page Title](file.md) ← link → nav entry under that section

    Top-level links (e.g. Glossary) become standalone nav entries.
    """
    current_section: str | None = None
    current_items: list = []
    nav: list = []

    def _flush():
        nonlocal current_section, current_items
        if current_section is not None:
            nav.append({current_section: current_items})
            current_section = None
            current_items = []

    for line in index_path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("-"):
            continue

        indent = len(line) - len(stripped)
        content = stripped[1:].strip()   # drop the leading "- "
        m = _LINK.match(content)

        if indent == 0:
            _flush()
            if m:
                title = _unescape(m.group(1))
                nav.append({title: f"guide/{m.group(2)}"})
            else:
                current_section = content
        elif m and current_section is not None:
            title = _unescape(m.group(1))
            current_items.append({title: f"guide/{m.group(2)}"})

    _flush()
    return nav


# ---------------------------------------------------------------------------
# MkDocs hook entry points
# ---------------------------------------------------------------------------

def on_pre_build(config) -> None:
    """
    Load Mermaid sources, copy + scrub guide Markdown with inline diagrams.
    Runs before MkDocs processes any pages.
    """
    if not GUIDE_SRC.exists():
        log.warning("Guide source not found: %s — skipping guide preparation", GUIDE_SRC)
        return

    mmd_map = _load_mmd_map()
    if mmd_map:
        log.info("Guide: loaded %d Mermaid diagram source(s)", len(mmd_map))
    else:
        log.warning("Guide: no .mmd files found in %s", IMAGES_SRC)

    _copy_and_scrub(mmd_map)


def on_config(config):
    """
    Inject a Guide section into the MkDocs nav.

    Reads from the *source* index so this works even on the very first build
    before on_pre_build has run in this process.
    """
    index_path = GUIDE_SRC / "index.md"
    if not index_path.exists():
        log.warning("Guide index not found: %s — skipping nav injection", index_path)
        return config

    guide_nav = _parse_nav(index_path)
    full_guide = [{"Overview": "guide/index.md"}] + guide_nav

    if config.get("nav") is None:
        config["nav"] = []
    config["nav"] = [
        item for item in config["nav"]
        if not (isinstance(item, dict) and "Guide" in item)
    ]
    config["nav"].append({"Guide": full_guide})

    return config
