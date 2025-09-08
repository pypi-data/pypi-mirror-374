#!/usr/bin/env python3
"""Generate an index page that links to sub coverage reports."""

from pathlib import Path

import click
from bs4 import BeautifulSoup


@click.command()
@click.option(
    "--dir",
    "htmlcov_dir",
    default="htmlcov",
    help="Coverage HTML output directory.",
)
def main(htmlcov_dir: str) -> None:
    """Generate top-level coverage index.

    Args:
        htmlcov_dir: The directory containing sub coverage reports.

    Raises:
        SystemExit: If the directory does not exist.

    """
    links: list[str] = []
    root = Path(htmlcov_dir)
    if not root.exists():
        click.echo(f"Directory '{htmlcov_dir}' does not exist.", err=True)
        raise SystemExit(1)

    for child in sorted(root.iterdir(), key=lambda p: p.name):
        index_file = child / "index.html"
        if child.is_dir() and index_file.exists():
            soup = BeautifulSoup(
                index_file.read_text(encoding="utf-8"),
                "html.parser",
            )
            coverage_span = soup.find("span", class_="pc_cov")
            coverage_text = coverage_span.text if coverage_span else "Unknown"
            content = (
                f'<li><a href="{child.name}/index.html">{child.name} Coverage Report</a><br/>'
                f"<p>Coverage report: {coverage_text}</p></li>"
            )
            links.append(content)

    links_html = "\n".join(links)
    content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Coverage Reports</title>
</head>
<body>
    <h1>Coverage Reports</h1>
    <ul>
        {links_html}
    </ul>
</body>
</html>"""

    index_path = root / "index.html"
    index_path.write_text(content, encoding="utf-8")
