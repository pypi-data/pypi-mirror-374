"""Script to update version in multiple files."""

import os
import re
import sys
from collections.abc import Callable
from pathlib import Path

version = os.environ.get("NEW_VERSION")
if not version:
    print("Error: NEW_VERSION environment variable not set.", file=sys.stderr)
    sys.exit(1)

files_to_update = [
    {
        "file": "uv.lock",
        "pattern": re.compile(
            r'(?P<block>version\s*=\s*["\'])(?P<version>[^\s"\']+)(["\'][^\[]*?source\s*=\s*{[^}]*?editable)',
            re.DOTALL,
        ),
        "replacement": lambda m: f"{m.group('block')}{version}{m.group(3)}",
    },
    {
        "file": "pyproject.toml",
        "pattern": re.compile(
            r'(?P<block>\[project\]\s+name\s*=\s*["\'].*?["\']\s+version\s*=\s*["\'])(?P<version>[^\s"\']+)(["\'])',
            re.DOTALL,
        ),
        "replacement": lambda m: f"{m.group('block')}{version}{m.group(3)}",
    },
    {
        "file": "docs/source/conf.py",
        "pattern": re.compile(
            r'(?P<block>version\s*=\s*["\'])(?P<version>[^\s"\']+)(["\']\s+release\s*=\s*["\'])(?P<release>[^\s"\']+)(["\'])',
            re.DOTALL,
        ),
        "replacement": lambda m: f"{m.group('block')}{version}"
        f"{m.group(3)}{version}{m.group(5)}",
    },
]

print(f"Updating version to: {version}\n")

for entry in files_to_update:
    filename = Path(entry["file"])
    pattern = entry["pattern"]
    replacement_func = entry["replacement"]
    updated = [False]

    print(f"Processing: {filename}")

    if not filename.exists():
        print("File not found, skipping.")
        continue

    try:
        content = filename.read_text(encoding="utf-8")

        def replacement_with_log(
            m: re.Match[str],
            replacement_func: Callable[[re.Match[str]], str] = replacement_func,
            updated_list: list[bool] = updated,
        ) -> str:
            """Log replacement operations and track updates."""
            old_line = m.group(0)
            new_line = replacement_func(m)
            if old_line.strip() != new_line.strip():
                updated_list[0] = True
                print(f"Matched:\n{old_line}\nReplaced with:\n{new_line}")
            return new_line

        new_content, num_replacements = pattern.subn(replacement_with_log, content)

        if num_replacements > 0:
            filename.write_text(new_content, encoding="utf-8")
            if updated[0]:
                print(f"Successfully updated version in {filename}\n")
            else:
                print("Already up-to-date\n")
        else:
            print("No matching version found, please check your regex or file.\n")
    except Exception as e:  # noqa: BLE001
        print(f"Error updating {filename}: {e}", file=sys.stderr)
