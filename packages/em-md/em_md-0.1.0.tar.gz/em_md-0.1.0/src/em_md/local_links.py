#!/usr/bin/env python3
"""
md_rel2abs.py — Rewrite relative Markdown links to absolute-from-project-root.

Features
- Rewrites Markdown inline links/images:   [txt](path)  ![alt](path)
- Rewrites reference-style definitions:     [id]: path "title"
- Rewrites common HTML embeds: <a href>, <img src>, <audio src>, <video src>, <source src>
- Skips inline code `like this` and fenced code blocks ``` ```
- Normalizes to POSIX-style forward slashes
- Output options:
    * root-absolute paths (default):   /docs/file.png
    * URL base:                        https://example.com/docs/file.png
    * file URLs:                       file:///abs/path/from/root/docs/file.png
- CLI with dry-run / write / backup, globbing, and ignore patterns.

Limitations
- Does not attempt to resolve Markdown link references across includes/macros.
- Does not “linkify” bare text URLs.
- Edge cases with exotic Markdown syntaxes are minimized but not impossible.
"""

from __future__ import annotations
import argparse
import fnmatch
import html
import os
import re
import sys
from pathlib import Path
from typing import Iterable, Tuple, Optional

# -----------------------
# Regex helpers (Markdown)
# -----------------------

# Fence and inline code masking:
FENCED_BLOCK_RE = re.compile(
    r"""
    (^|\n)                # line start
    (?P<fence>`{3,}|~{3,}) # opening fence (``` or ~~~)
    [^\n]*\n               # rest of opening line
    (?:.*?\n)*?            # block content, non-greedy, multiline
    (?P=fence)[ \t]*\n?    # matching closing fence
    """,
    re.VERBOSE,
)

INLINE_CODE_RE = re.compile(
    # match equal number of backticks, not followed by another `
    r"(`+)([^`]*?)\1(?!`)",
)

# turn into two patterns: image and normal link
# Markdown inline images:
MD_IMAGE_RE = re.compile(
    r"""
    !\[([^\]]*)\]        # ![alt text]
    \(                   # (
      \s*
      (?P<url>[^)\s]+)   # URL until space or ')'
      (?:\s+("([^"]*)"|'([^']*)'))?  # optional quoted title
      \s*
    \)                   # )
    """,
    re.VERBOSE,
)

# Markdown inline links:
MD_INLINE_LINK_RE = re.compile(
    r"""
    \[([^\]]*)\]         # [link text]
    \(                   # (
      \s*
      (?P<url>[^)\s]+)   # URL until space or ')'
      (?:\s+("([^"]*)"|'([^']*)'))?  # optional quoted title
      \s*
    \)                   # )
    """,
    re.VERBOSE,
)

# Reference-style definitions:
#   [label]: url "title"
MD_REFDEF_RE = re.compile(
    r"""
    ^\s*\[([^\]]+)\]:      # [label]:
    \s*
    (?P<url>\S+)           # url
    (?:\s+("([^"]*)"|'([^']*)'))?  # optional title
    \s*$
    """,
    re.MULTILINE | re.VERBOSE,
)

# -----------------------
# HTML attribute rewriting
# -----------------------

HTML_ATTRS = ("href", "src")
HTML_TAGS = ("a", "img", "audio", "video", "source")

HTML_TAG_RE = re.compile(
    r"""
    <(?P<tag>a|img|audio|video|source)\b
    (?P<attrs>[^>]*?)
    >
    """,
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)

HTML_ATTR_RE = re.compile(
    r"""\b(?P<name>href|src)\s*=\s*(['"])(?P<val>.*?)(\2)""",
    re.IGNORECASE | re.DOTALL,
)

# -----------------------
# URL helpers
# -----------------------


def is_absolute_path(url: str) -> bool:
    """Heuristic: relative if it doesn’t start with a scheme, #, mailto:, data:, //, or / (for project-root absolute we *do* consider / absolute)."""
    u = url.strip()
    if u.startswith("/"):
        return True
    return False


def is_relative_path(url: str) -> bool:
    """Heuristic: relative if it doesn’t start with a scheme, #, mailto:, data:, //, or / (for project-root absolute we *do* consider / absolute)."""
    u = url.strip()
    if not u:
        return False
    if u.startswith("#"):
        return False
    if u.startswith(
        ("http://", "https://", "ftp://", "mailto:", "tel:", "data:", "file://")
    ):
        return False
    if u.startswith("//"):  # protocol-relative
        return False
    if u.startswith("/"):  # already root-absolute
        return False
    return True


def to_root_absolute(
    url: str, root: Path, file_dir: Path, url_base: Optional[str], file_urls: bool
) -> str:
    """
    Turn relative 'url' used in 'file_dir' into a root-absolute path.
    - If 'url_base' provided, prefix with that (e.g., https://example.com)
    - If 'file_urls' True, produce file:///… URLs for the resolved path.
    - Otherwise return "/path/from/project/root".
    """
    # Support angle-bracketed paths <...> (rare but allowed)
    wrapped = url.startswith("<") and url.endswith(">")
    core = url[1:-1] if wrapped else url

    # Normalize filesystem path
    # Keep query/fragment if present (e.g., img.png?ver=1#frag)
    path_part, qfrag = split_query_fragment(core)

    # Resolve relative to the current file directory
    abs_fs = (file_dir / path_part).resolve()

    # Ensure inside project root; if not, keep original URL
    try:
        rel_to_root = abs_fs.relative_to(root)
    except ValueError:
        return url  # outside root; leave untouched

    posix_rel = "/".join(rel_to_root.parts)

    if url_base:
        new = url_base.rstrip("/") + "/" + posix_rel.lstrip("/")
    elif file_urls:
        # Produce file:/// URLs with POSIX separators
        new = "file://" + "/" + "/".join(abs_fs.parts)
    else:
        new = "/" + posix_rel.lstrip("/")

    if qfrag:
        new += qfrag

    return f"<{new}>" if wrapped else new


def to_relative(url: str, root: Path, file_dir: Path) -> str:
    """
    Convert a root-absolute (/foo/bar.png) or file:/// path that points
    inside the project into a relative path from file_dir.
    """
    wrapped = url.startswith("<") and url.endswith(">")
    core = url[1:-1] if wrapped else url

    path_part, qfrag = split_query_fragment(core)

    # Handle file://
    if core.startswith("file://"):
        abs_fs = Path(core[7:]).resolve()
    elif core.startswith("/"):  # root-absolute
        abs_fs = (root / path_part.lstrip("/")).resolve()
    else:
        return url  # not an absolute we handle

    if not abs_fs.exists():
        return url  # leave it untouched if the file doesn’t exist

    rel = os.path.relpath(abs_fs, start=file_dir)
    new = rel.replace(os.sep, "/")  # POSIX style
    if qfrag:
        new += qfrag
    return f"<{new}>" if wrapped else new


def split_query_fragment(s: str) -> Tuple[str, str]:
    # Split off ?query and/or #fragment conservatively
    m = re.match(r"^(.*?)([\?#].*)$", s)
    if m:
        return m.group(1), m.group(2)
    return s, ""


# -----------------------
# Core rewriting
# -----------------------


MASK = "\uffff"


def mask_code(text: str) -> tuple[str, list[str]]:
    masked = []
    counter = 0

    def _store(m):
        nonlocal counter
        masked.append(m.group(0))
        token = f"{MASK}{counter}{MASK}"
        counter += 1
        return token

    text = FENCED_BLOCK_RE.sub(_store, text)
    text = INLINE_CODE_RE.sub(_store, text)
    return text, masked


def unmask_code(text: str, masked: list[str]) -> str:
    for i, chunk in enumerate(masked):
        token = f"{MASK}{i}{MASK}"
        text = text.replace(token, chunk, 1)
    return text


def rewrite_markdown(
    text: str,
    root: Path,
    file_dir: Path,
    url_base: Optional[str],
    file_urls: bool,
    mode: str = "to-absolute",
) -> str:
    masked_text, masked_chunks = mask_code(text)

    match mode:
        case "to-absolute":

            def url_rewriter(u):
                return to_root_absolute(u, root, file_dir, url_base, file_urls)

            def need_to_change_url(u):
                return is_relative_path(u)
        case "to-relative":

            def url_rewriter(u):
                return to_relative(u, root, file_dir)

            def need_to_change_url(u):
                return is_absolute_path(u)
        case _:
            raise ValueError(
                f"mode must be 'to-absolute' or 'to-relative', not '{mode}'"
            )

    # Inline images
    def _img_sub(m: re.Match) -> str:
        full = m.group(0)
        url = m.group("url")
        return full.replace(url, url_rewriter(url)) if need_to_change_url(url) else full

    # Inline links
    def _link_sub(m: re.Match) -> str:
        full = m.group(0)
        url = m.group("url")
        return full.replace(url, url_rewriter(url)) if need_to_change_url(url) else full

    work = MD_IMAGE_RE.sub(_img_sub, masked_text)
    work = MD_INLINE_LINK_RE.sub(_link_sub, work)

    # Reference-style definitions
    def _refdef_sub(m: re.Match) -> str:
        full = m.group(0)
        url = m.group("url")
        if not need_to_change_url(url):
            return full
        new = url_rewriter(url)
        return full.replace(url, new, 1)

    work = MD_REFDEF_RE.sub(_refdef_sub, work)

    # HTML tags/attrs
    def _html_tag_sub(m: re.Match) -> str:
        tag = m.group("tag")
        attrs = m.group("attrs")

        def _attr_sub(a: re.Match) -> str:
            name = a.group("name")
            val = a.group("val")
            if need_to_change_url(val):
                new_val = url_rewriter(val)
                return f'{name}="{html.escape(new_val, quote=True)}"'
            return a.group(0)

        new_attrs = HTML_ATTR_RE.sub(_attr_sub, attrs)
        return f"<{tag}{new_attrs}>"

    work = HTML_TAG_RE.sub(_html_tag_sub, work)

    return unmask_code(work, masked_chunks)


# -----------------------
# CLI
# -----------------------


def iter_files(
    root: Path, patterns: Iterable[str], ignore: Iterable[str]
) -> Iterable[Path]:
    all_files = set()
    for pat in patterns:
        for p in root.glob(pat):
            if p.is_file():
                rel = str(p.relative_to(root))
                if any(fnmatch.fnmatch(rel, ig) for ig in ignore):
                    continue
                all_files.add(p)
    for p in sorted(all_files):
        yield p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Rewrite relative Markdown links to root-absolute."
    )
    ap.add_argument("--root", type=Path, required=True, help="Project root directory.")
    ap.add_argument(
        "--mode",
        choices=["to-absolute", "to-relative"],
        default="to-absolute",
        help="Rewrite direction (default: to-absolute).",
    )
    ap.add_argument(
        "--glob",
        action="append",
        default=["**/*.md"],
        help="Glob(s) to include (default **/*.md).",
    )
    ap.add_argument("--ignore", action="append", default=[], help="Glob(s) to ignore.")
    ap.add_argument(
        "--url-base",
        default=None,
        help="If set, prefix with this base (e.g., https://example.com).",
    )
    ap.add_argument(
        "--file-urls",
        action="store_true",
        help="Output file:/// URLs instead of /root paths.",
    )
    ap.add_argument("--write", action="store_true", help="Rewrite files in place.")
    ap.add_argument(
        "--backup", action="store_true", help="Keep .bak backups when writing."
    )
    ap.add_argument(
        "--print-changes",
        action="store_true",
        help="Print a unified diff-like summary of changes.",
    )
    args = ap.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"[error] --root must be a directory: {root}", file=sys.stderr)
        return 2

    changed_any = False

    for path in iter_files(root, args.glob, args.ignore):
        orig = path.read_text(encoding="utf-8")
        new = rewrite_markdown(
            orig,
            root=root,
            file_dir=path.parent.resolve(),
            url_base=args.url_base,
            file_urls=args.file_urls,
            mode=args.mode,
        )

        if orig != new:
            changed_any = True
            if args.print_changes:
                print(f"--- {path}")
                print(f"+++ {path}")
                # simple line-by-line difference preview
                import difflib

                for line in difflib.unified_diff(
                    orig.splitlines(), new.splitlines(), lineterm=""
                ):
                    print(line)
            if args.write:
                if args.backup:
                    backup = path.with_suffix(path.suffix + ".bak")
                    backup.write_text(orig, encoding="utf-8")
                path.write_text(new, encoding="utf-8")

    if not changed_any:
        print("No changes needed.")
    else:
        if not args.write:
            print("Changes detected. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
