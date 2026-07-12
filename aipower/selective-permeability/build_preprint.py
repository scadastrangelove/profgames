#!/usr/bin/env python3
"""Build the self-contained publication HTML and A4 PDF."""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import markdown
except ImportError as exc:
    raise SystemExit(
        "Python-Markdown is required. Install requirements-publication.txt first."
    ) from exc


ROOT = Path(__file__).resolve().parent
TITLE = (
    "Selective Permeability: A Behavioral-Security Metric for LLM Advisors, "
    "with Two Failure Modes of In-Context Provenance Workflows"
)

CSS = r"""
:root {
  --ink: #171918;
  --muted: #58605d;
  --line: #cfd5d2;
  --accent: #176b58;
  --soft: #f3f6f4;
}
* { box-sizing: border-box; }
html { font-size: 16px; }
body {
  max-width: 900px;
  margin: 0 auto;
  padding: 52px 48px 90px;
  color: var(--ink);
  background: #fff;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 11.2pt;
  line-height: 1.48;
}
h1, h2, h3, h4 {
  color: #111514;
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 650;
  line-height: 1.2;
}
h1 {
  margin: 0 0 18px;
  padding-top: 18px;
  border-top: 5px solid var(--accent);
  font-size: 24pt;
  letter-spacing: 0;
}
h2 {
  margin: 30px 0 12px;
  padding-bottom: 5px;
  border-bottom: 1px solid var(--line);
  font-size: 15pt;
}
h3 { margin: 24px 0 8px; font-size: 12.2pt; }
h4 { margin: 20px 0 7px; font-size: 11pt; }
p { margin: 8px 0; }
.byline {
  margin: 0 0 26px;
  color: var(--muted);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 10pt;
  line-height: 1.55;
}
a { color: var(--accent); text-decoration: none; overflow-wrap: anywhere; }
a:hover { text-decoration: underline; }
strong { color: #0d0f0e; }
code {
  padding: 1px 3px;
  border-radius: 2px;
  background: var(--soft);
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 0.84em;
  overflow-wrap: anywhere;
}
blockquote {
  margin: 12px 0;
  padding: 4px 14px;
  border-left: 3px solid var(--accent);
  color: var(--muted);
  background: var(--soft);
}
ul, ol { padding-left: 24px; }
li { margin: 4px 0; }
table {
  width: 100%;
  margin: 13px 0 17px;
  border-collapse: collapse;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.2pt;
  line-height: 1.28;
}
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td {
  padding: 4px 5px;
  border: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
  overflow-wrap: anywhere;
}
th { background: #e9efec; font-weight: 650; }
tbody tr:nth-child(even) td { background: #f8faf9; }
figure {
  margin: 18px auto 22px;
  break-inside: avoid;
}
figure img {
  display: block;
  width: auto;
  max-width: 100%;
  max-height: 215mm;
  margin: 0 auto;
  border: 1px solid #e2e7e4;
}
.figure-2 img { max-width: 70%; }
figcaption {
  margin: 7px auto 0;
  color: #3f4744;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.7pt;
  line-height: 1.35;
}
.page-break { break-before: page; }
#references + ol { font-size: 9.3pt; line-height: 1.38; }
#references + ol li { margin-bottom: 7px; }
h2[id^="appendix-a-"] + p + table { break-inside: avoid; }
@page {
  size: A4;
  margin: 17mm 17mm 19mm;
  @top-right {
    content: "Selective Permeability";
    color: #69716e;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 7.5pt;
  }
  @bottom-center {
    content: counter(page);
    color: #69716e;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 8pt;
  }
}
@media print {
  html { font-size: 12px; }
  body {
    max-width: none;
    margin: 0;
    padding: 0;
    font-size: 9.55pt;
    line-height: 1.39;
  }
  h1 { font-size: 21pt; }
  h2 { margin-top: 23px; font-size: 13.5pt; break-after: avoid-page; }
  h3 { margin-top: 18px; font-size: 11pt; break-after: avoid-page; }
  h4 { break-after: avoid-page; }
  p, li { orphans: 3; widows: 3; }
  a { color: var(--ink); }
  table { font-size: 7.35pt; }
  h2[id^="t3b-"] { break-before: page; }
  figure { margin: 12px auto 15px; }
  figcaption { font-size: 7.7pt; }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html-only", action="store_true", help="Do not render PDF")
    parser.add_argument("--chrome", help="Path to a Chromium/Chrome executable")
    return parser.parse_args()


def combine_sources() -> str:
    main = (ROOT / "preprint.md").read_text(encoding="utf-8").rstrip()
    tables = (ROOT / "tables" / "TABLES.md").read_text(encoding="utf-8").strip()
    references = (ROOT / "references.md").read_text(encoding="utf-8").strip()
    separator = '\n\n<div class="page-break"></div>\n\n'
    return separator.join((main, tables, references)) + "\n"


def wrap_figures(body: str) -> str:
    pattern = re.compile(
        r'<p><img alt="([^"]*)" src="([^"]+)"\s*/?></p>\s*'
        r'<p><em>(Figure\s+\d+\..*?)</em></p>',
        re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        alt, src, caption = match.groups()
        caption = re.sub(r"\s+", " ", caption).strip()
        figure_number = re.match(r"Figure\s+(\d+)\.", caption)
        figure_class = f" figure-{figure_number.group(1)}" if figure_number else ""
        return (
            f'<figure class="figure{figure_class}"><img alt="{alt}" src="{src}">'
            f"<figcaption>{caption}</figcaption></figure>"
        )

    return pattern.sub(replace, body)


def inline_images(body: str) -> str:
    pattern = re.compile(r'(<img\b[^>]*\bsrc=")([^"]+)(")')

    def replace(match: re.Match[str]) -> str:
        prefix, src, suffix = match.groups()
        if src.startswith(("data:", "http://", "https://")):
            return match.group(0)
        path = (ROOT / src).resolve()
        if not path.is_file() or ROOT not in path.parents:
            raise FileNotFoundError(f"Image not found or outside release: {src}")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        payload = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'{prefix}data:{mime};base64,{payload}{suffix}'

    return pattern.sub(replace, body)


def render_html(source: str) -> str:
    body = markdown.markdown(
        source,
        extensions=("extra", "sane_lists", "toc"),
        output_format="html5",
    )
    body = wrap_figures(body)
    body = inline_images(body)
    body = body.replace(
        "<p><strong>Sergey Gordeychik</strong>",
        '<p class="byline"><strong>Sergey Gordeychik</strong>',
        1,
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Sergey Gordeychik">
  <meta name="description" content="A behavioral-security study of selective permeability in LLM advisors.">
  <title>{html.escape(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def find_chrome(explicit: str | None) -> str:
    candidates = [
        explicit,
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise SystemExit("Chrome/Chromium not found; use --chrome or build with --html-only.")


def render_pdf(chrome: str, html_path: Path, pdf_path: Path) -> None:
    command = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=1500",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise SystemExit("Chrome completed without creating a PDF.")


def main() -> None:
    args = parse_args()
    source = combine_sources()
    html_text = render_html(source)
    html_path = ROOT / "preprint.html"
    html_path.write_text(html_text, encoding="utf-8")
    print(f"wrote {html_path} ({html_path.stat().st_size:,} bytes)")
    if not args.html_only:
        pdf_path = ROOT / "preprint.pdf"
        render_pdf(find_chrome(args.chrome), html_path, pdf_path)
        print(f"wrote {pdf_path} ({pdf_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
