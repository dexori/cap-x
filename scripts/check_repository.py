#!/usr/bin/env python3
"""Fast, hardware-independent integrity checks for the public repository."""

from __future__ import annotations

import configparser
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "THIRD_PARTY.md",
    "CITATION.cff",
    "pyproject.toml",
    "uv.lock",
)
PUBLIC_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "THIRD_PARTY.md",
    "docs/reproducibility.md",
)
REQUIRED_CONFIG_KEYS = {"env", "output_dir", "trials", "num_workers"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key {key!r} on line {key_node.start_mark.line + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def _check_markdown_links(path: Path) -> list[str]:
    errors: list[str] = []
    for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        local_part = unquote(target.split("#", 1)[0])
        destination = (path.parent / local_part).resolve()
        if ROOT not in destination.parents and destination != ROOT:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
        elif not destination.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link: {target}")
    return errors


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if not isinstance(pyproject["project"].get("dependencies"), list):
        errors.append("pyproject.toml project.dependencies must be a list")
    if not isinstance(pyproject["project"].get("urls"), dict):
        errors.append("pyproject.toml project.urls must be a table")
    project_version = pyproject["project"]["version"]
    init_text = (ROOT / "capx/__init__.py").read_text(encoding="utf-8")
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.MULTILINE)
    if not version_match or version_match.group(1) != project_version:
        errors.append("pyproject.toml and capx/__init__.py versions do not match")

    citation = yaml.load(
        (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
        Loader=UniqueKeyLoader,
    )
    if not isinstance(citation, dict) or str(citation.get("version")) != project_version:
        errors.append("CITATION.cff version does not match pyproject.toml")

    configs = sorted((ROOT / "env_configs").rglob("*.yaml"))
    if not configs:
        errors.append("no benchmark configs found under env_configs/")
    for path in configs:
        try:
            document = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{path.relative_to(ROOT)}: top-level YAML value must be a mapping")
            continue
        missing = REQUIRED_CONFIG_KEYS - document.keys()
        if missing:
            errors.append(
                f"{path.relative_to(ROOT)}: missing required keys: {', '.join(sorted(missing))}"
            )

    modules = configparser.ConfigParser()
    modules.read(ROOT / ".gitmodules")
    for section in modules.sections():
        url = modules[section].get("url", "")
        if not url.startswith("https://"):
            errors.append(f"{section}: submodule URL must use HTTPS")

    for relative in PUBLIC_DOCS:
        errors.extend(_check_markdown_links(ROOT / relative))

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    sensitive_names = {".env", ".openrouterkey", ".nvinferencekeys", "credentials.json"}
    for name in tracked:
        if Path(name).name.lower() in sensitive_names:
            errors.append(f"potential credential file is tracked: {name}")

    if errors:
        print("Repository checks failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Repository checks passed ({len(configs)} benchmark configs validated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
