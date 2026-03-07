#!/usr/bin/env python3
"""Minimal skill architecture audit for this repository.

Checks:
- each top-level skill dir has SKILL.md
- SKILL.md has frontmatter with name + description
- frontmatter name matches directory name
- skill exists in catalog/skills.yaml
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = ROOT / "catalog" / "skills.yaml"
IGNORE_DIRS = {".git", "catalog", "docs", "scripts", "__pycache__"}
NAME_MISMATCH_ALLOWLIST = {
    "self-improving": "Self-Improving Agent (With Self-Reflection)",
}


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return {}

    frontmatter = m.group(1)
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        if line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def parse_catalog_names() -> set[str]:
    if not CATALOG_FILE.exists():
        return set()

    names: set[str] = set()
    for line in CATALOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- name:"):
            names.add(line.split(":", 1)[1].strip())
    return names


def main() -> int:
    issues: list[str] = []
    warnings: list[str] = []
    catalog_names = parse_catalog_names()

    skill_dirs = [
        p
        for p in sorted(ROOT.iterdir())
        if p.is_dir() and p.name not in IGNORE_DIRS and not p.name.startswith(".")
    ]

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            issues.append(f"{skill_dir.name}: missing SKILL.md")
            continue

        fm = parse_frontmatter(skill_md)
        name = fm.get("name")
        desc = fm.get("description")

        if not name:
            issues.append(f"{skill_dir.name}: frontmatter missing 'name'")
        elif name != skill_dir.name:
            allowed = NAME_MISMATCH_ALLOWLIST.get(skill_dir.name)
            if allowed != name:
                warnings.append(
                    f"{skill_dir.name}: frontmatter name '{name}' does not match directory"
                )

        if not desc:
            issues.append(f"{skill_dir.name}: frontmatter missing 'description'")

        if skill_dir.name not in catalog_names:
            issues.append(f"{skill_dir.name}: missing from catalog/skills.yaml")

    if issues:
        print("❌ Skill audit failed:\n")
        for issue in issues:
            print(f"- {issue}")
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    print(f"✅ Skill audit passed ({len(skill_dirs)} skills checked)")
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
