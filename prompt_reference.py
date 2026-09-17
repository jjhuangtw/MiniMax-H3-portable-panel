"""Load MiniMax's official h3-prompt-writing reference guides and expose them as
browsable prompt-library categories: the T2VA/I2VA/FL2VA/L2VA three-field guide and
the Ref2VA six-section guide, each split verbatim into its numbered sections.

Source (vendored under prompt_references/, unmodified):
https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.claude/skills/h3-prompt-writing
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(BASE_DIR, "prompt_references")


def _read(name):
    try:
        with open(os.path.join(REF_DIR, name), encoding="utf-8") as stream:
            return stream.read()
    except OSError:
        return ""


def _split_sections(text):
    """Split a guide at its level-2 `## ` headers into an ordered {title: body} map.
    Text before the first `## ` (the file title and intro) becomes a leading entry."""
    if not text.strip():
        return {}
    parts = re.split(r"(?m)^## +", text)
    sections = {}
    intro = parts[0].strip()
    if intro:
        title = intro.splitlines()[0].lstrip("# ").strip()
        sections[f"｜總覽｜ {title}"] = intro
    for part in parts[1:]:
        head = part.splitlines()[0].strip()
        sections[head] = "## " + part.rstrip()
    return sections


def _explode_cases(sections):
    """Break a 'Cases' section into one entry per `### ` case, so each worked example
    is individually browsable and can be applied as a starting prompt."""
    out = {}
    for title, body in sections.items():
        if "Case" in title and re.search(r"(?m)^### ", body):
            for chunk in re.split(r"(?m)^### +", body)[1:]:
                sub = chunk.splitlines()[0].strip()
                out[f"{title} · {sub}"] = "### " + chunk.rstrip()
        else:
            out[title] = body
    return out


_BASE = _explode_cases(_split_sections(_read("base-en.txt")))
_REF = _split_sections(_read("ref-en.txt"))

# Category name -> {entry title: verbatim section text}; empty if a file is missing.
OFFICIAL_GUIDE_CATEGORIES = {}
if _BASE:
    OFFICIAL_GUIDE_CATEGORIES["📖 官方指南｜三段格式 T2VA/I2VA/FL2VA/L2VA"] = _BASE
if _REF:
    OFFICIAL_GUIDE_CATEGORIES["📖 官方指南｜Ref 六段格式（全參考 Ref2VA）"] = _REF
