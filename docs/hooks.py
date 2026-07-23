"""MkDocs build hooks for agent skill discovery files.

Copies ``.agents/skills/*/SKILL.md`` files into the built site under
``.well-known/agent-skills/`` and generates two discovery catalogs:

- ``.well-known/agent-skills/index.json`` – the agent skills discovery format.
- ``.well-known/ai-catalog.json`` – the AI catalog format.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# --- Constants ---------------------------------------------------------------

SKILLS_DIR = Path(__file__).parent.parent / ".agents" / "skills"
"""Where skill source files live in the repo."""

WELL_KNOWN_DIR = ".well-known/agent-skills"
"""Output directory for skills, relative to the site directory."""

CATALOG_FILENAME = ".well-known/ai-catalog.json"
"""Name of the AI catalog file, relative to the site directory."""

HOST_DISPLAY_NAME = "wagtail-personalisation"
HOST_IDENTIFIER = "did:web:wagtail-nest.github.io"
HOST_DOCUMENTATION_URL = "https://wagtail-nest.github.io/wagtail-personalisation/"
SKILL_TYPE = "skill-md"
SKILL_MIME = "application/agent-skills+md"
SKILL_VERSION = "1.0.0"


# --- Helpers -----------------------------------------------------------------


def _parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from a Markdown file's content."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def _sha256(path: Path) -> str:
    """Compute the ``sha256:...`` digest of a file."""
    h = hashlib.sha256(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _iso_date(path: Path) -> str:
    """Format a file's last-modified time as ``YYYY-MM-DDTHH:MM:SSZ``."""
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.strftime("%Y-%m-%dT00:00:00Z")


def _read_version() -> str:
    """Read ``__version__`` from the package without importing it."""
    init = (
        Path(__file__).parent.parent / "src" / "wagtail_personalisation" / "__init__.py"
    )
    for line in init.read_text().splitlines():
        if line.startswith("__version__"):
            return str(line.split("=", 1)[1].strip().strip('"').strip("'"))
    return SKILL_VERSION


def _discover_skills() -> list[Path]:
    """Find every ``SKILL.md`` under ``.agents/skills/``."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def _site_root(config: dict[str, Any]) -> str:
    """Return the site's root URL, with a trailing slash stripped."""
    return str(config.get("site_url", "")).rstrip("/")


# --- Hook --------------------------------------------------------------------


def on_post_build(config: dict[str, Any], **kwargs: Any) -> None:
    """Copy skill files and generate discovery catalogs after the build."""
    site_dir = Path(config["site_dir"])
    site_root = _site_root(config)

    # Directory where the skills land in the built site.
    skills_out = site_dir / WELL_KNOWN_DIR
    skills_out.mkdir(parents=True, exist_ok=True)

    # Discover and copy all SKILL.md files.
    index_entries: list[dict[str, Any]] = []
    catalog_entries: list[dict[str, Any]] = []
    host: dict[str, str] = {
        "displayName": HOST_DISPLAY_NAME,
        "identifier": HOST_IDENTIFIER,
        "documentationUrl": HOST_DOCUMENTATION_URL,
    }

    for skill_path in _discover_skills():
        name = skill_path.parent.name
        target_dir = skills_out / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "SKILL.md"
        shutil.copy2(skill_path, target)

        # Parse frontmatter for metadata.
        frontmatter = _parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        description = frontmatter.get("description", "")
        digest = _sha256(skill_path)
        updated_at = _iso_date(skill_path)

        # Root-relative path within the site.
        rel_path = f"{WELL_KNOWN_DIR}/{name}/SKILL.md"
        full_url = f"{site_root}/{rel_path}"

        index_entries.append(
            {
                "name": name,
                "type": SKILL_TYPE,
                "description": description,
                "url": f"/{rel_path}",
                "digest": digest,
            }
        )
        catalog_entries.append(
            {
                "identifier": f"urn:air:wagtail-nest.github.io:skill:{name}",
                "displayName": name,
                "type": SKILL_MIME,
                "url": full_url,
                "description": description,
                "version": _read_version(),
                "updatedAt": updated_at,
                "publisher": host,
            }
        )

    # Write the agent-skills discovery index.
    index = {
        "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
        "skills": index_entries,
    }
    (skills_out / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Write the AI catalog.
    catalog = {
        "specVersion": "1.0",
        "host": host,
        "entries": catalog_entries,
    }
    (site_dir / CATALOG_FILENAME).write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
