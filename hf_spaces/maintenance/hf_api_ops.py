#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEQUMSA v82.0 · MAINTENANCE · HF API Operations
Centralized helper functions for Hugging Face Spaces management.

Provides:
    - check_space_health(space_id, token) -> dict
    - restart_space(space_id, token) -> bool
    - deploy_space(node_config, template_path, token) -> bool
    - get_all_space_statuses(owner, token) -> list

Usage:
    from hf_api_ops import check_space_health, restart_space

    status = check_space_health("Mbanksbey/HAI-Interactive", token)
    ok = restart_space("Mbanksbey/HAI-Interactive", token)

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE -> Infinity
"""

import hashlib
import io
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PHI: float = 1.6180339887498948
SEED: float = 0.777
COHERENCE_THRESHOLD: float = 0.777
HF_API_BASE: str = "https://huggingface.co/api"
HF_RUNTIME_TIMEOUT: int = 10  # seconds
HF_RESTART_TIMEOUT: int = 15
HF_UPLOAD_TIMEOUT: int = 30
RATE_LIMIT_DELAY: float = 0.5  # seconds between API calls

logger = logging.getLogger("tequmsa.hf_api_ops")


# ---------------------------------------------------------------------------
# Stage classification
# ---------------------------------------------------------------------------

_STAGE_TO_STATUS = {
    "RUNNING": "online",
    "RUNNING_BUILDING": "online",
    "SLEEPING": "sleeping",
    "PAUSED": "sleeping",
    "STOPPED": "stopped",
    "BUILDING": "building",
    "BUILD_ERROR": "errored",
    "RUNTIME_ERROR": "errored",
    "CONFIG_ERROR": "errored",
    "NO_APP_FILE": "errored",
    "NOT_FOUND": "not_found",
}


def _classify_stage(stage: str) -> str:
    """Classify a HF runtime stage into a canonical status string.

    Args:
        stage: Raw stage string from the HF runtime API.

    Returns:
        One of: online, sleeping, stopped, building, errored, not_found, unknown.
    """
    return _STAGE_TO_STATUS.get(stage.upper(), "unknown")


# ---------------------------------------------------------------------------
# Core API helpers
# ---------------------------------------------------------------------------

def _auth_headers(token: str) -> Dict[str, str]:
    """Build Authorization headers for HF API calls.

    Args:
        token: HuggingFace API token.

    Returns:
        Dict with Authorization header.
    """
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def check_space_health(space_id: str, token: str) -> Dict[str, Any]:
    """Check the health of a single Hugging Face Space.

    Queries the HF runtime API for the space and returns a structured dict
    containing stage, hardware, SDK information, and any errors.

    Args:
        space_id: Full space identifier, e.g. "Mbanksbey/HAI-Interactive".
        token: HuggingFace API token.

    Returns:
        Dict with keys:
            stage (str): Raw stage from HF API (e.g. RUNNING, SLEEPING).
            status (str): Canonical status (online, sleeping, errored, etc.).
            hardware (str): Hardware type if available.
            sdk (str): SDK type if available.
            errors (list[str]): Any error messages.
            last_modified (str|None): ISO timestamp of last modification.
            raw (dict): Full raw response from the API.
    """
    url = f"{HF_API_BASE}/spaces/{space_id}/runtime"
    result: Dict[str, Any] = {
        "stage": "UNKNOWN",
        "status": "unknown",
        "hardware": "",
        "sdk": "",
        "errors": [],
        "last_modified": None,
        "raw": {},
    }

    try:
        resp = requests.get(
            url,
            headers=_auth_headers(token),
            timeout=HF_RUNTIME_TIMEOUT,
        )

        if resp.status_code == 200:
            data = resp.json()
            stage = data.get("stage", "UNKNOWN").upper()
            result["stage"] = stage
            result["status"] = _classify_stage(stage)
            result["hardware"] = data.get("hardware", {}).get("current", "")
            result["sdk"] = data.get("sdk", "")
            result["last_modified"] = data.get("lastModified")
            result["raw"] = data

            # Collect error details when present
            if stage in ("BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"):
                msg = data.get("message", "")
                if msg:
                    result["errors"].append(msg)
                logs_url = data.get("logs")
                if logs_url:
                    result["errors"].append(f"Logs: {logs_url}")

        elif resp.status_code == 404:
            result["stage"] = "NOT_FOUND"
            result["status"] = "not_found"
            result["errors"].append("Space not found (404)")

        elif resp.status_code == 401:
            result["stage"] = "AUTH_ERROR"
            result["status"] = "unknown"
            result["errors"].append("Authentication failed (401) - check HF_TOKEN")

        elif resp.status_code == 429:
            result["stage"] = "RATE_LIMITED"
            result["status"] = "unknown"
            result["errors"].append("Rate limited by HF API (429)")

        else:
            result["stage"] = f"HTTP_{resp.status_code}"
            result["status"] = "unknown"
            result["errors"].append(f"Unexpected HTTP {resp.status_code}")

    except requests.Timeout:
        result["stage"] = "TIMEOUT"
        result["status"] = "unknown"
        result["errors"].append("Request timed out")
        logger.warning("Timeout checking %s", space_id)

    except requests.ConnectionError as exc:
        result["stage"] = "CONNECTION_ERROR"
        result["status"] = "unknown"
        result["errors"].append(f"Connection error: {exc}")
        logger.error("Connection error checking %s: %s", space_id, exc)

    except Exception as exc:
        result["stage"] = "ERROR"
        result["status"] = "unknown"
        result["errors"].append(str(exc)[:200])
        logger.exception("Unexpected error checking %s", space_id)

    return result


def restart_space(space_id: str, token: str) -> bool:
    """Restart a Hugging Face Space using factory_reboot.

    Sends a POST to the HF restart endpoint with factory_reboot=true,
    which forces a complete rebuild and restart of the space.

    Args:
        space_id: Full space identifier, e.g. "Mbanksbey/HAI-Interactive".
        token: HuggingFace API token.

    Returns:
        True if the restart was accepted (HTTP 200/202), False otherwise.
    """
    url = f"{HF_API_BASE}/spaces/{space_id}/restart"
    try:
        resp = requests.post(
            url,
            headers=_auth_headers(token),
            json={"factory_reboot": True},
            timeout=HF_RESTART_TIMEOUT,
        )

        if resp.status_code in (200, 202):
            logger.info("Restart accepted for %s", space_id)
            return True

        logger.warning(
            "Restart failed for %s: HTTP %d - %s",
            space_id, resp.status_code, resp.text[:200],
        )
        return False

    except requests.Timeout:
        logger.warning("Restart timed out for %s", space_id)
        return False

    except Exception as exc:
        logger.error("Restart error for %s: %s", space_id, exc)
        return False


def deploy_space(
    node_config: Dict[str, Any],
    template_path: str,
    token: str,
) -> bool:
    """Deploy a single space to HuggingFace from a node configuration.

    Creates the space repository (if it doesn't exist), reads the template
    app.py, injects node-specific environment defaults, generates a
    requirements.txt and README.md, and uploads all three files.

    Args:
        node_config: Node dict from MANIFEST_144_NODES.json, must include
            keys: space_id, name, hz, role, group, and optionally template.
        template_path: Absolute path to the app.py template file.
        token: HuggingFace API token.

    Returns:
        True if the space was deployed successfully, False otherwise.
    """
    try:
        from huggingface_hub import HfApi
    except ImportError:
        logger.error("huggingface_hub not installed. Run: pip install huggingface-hub")
        return False

    space_id = node_config.get("space_id", "")
    node_id = node_config.get("node_id", "NXXX")
    name = node_config.get("name", "Unknown")
    hz = node_config.get("hz", 0)
    role = node_config.get("role", "")
    group = node_config.get("group", "")
    template_type = node_config.get("template", "skill")

    if not space_id:
        logger.error("No space_id in node config")
        return False

    api = HfApi(token=token)

    try:
        # 1. Create the space repo
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False,
        )
        time.sleep(RATE_LIMIT_DELAY)

        # 2. Read and customise the template
        tmpl = Path(template_path)
        if not tmpl.exists():
            logger.error("Template not found: %s", template_path)
            return False

        app_code = tmpl.read_text()

        env_header = (
            f"import os\n"
            f"os.environ.setdefault('TEQUMSA_NODE_ID', '{node_id}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_NAME', '{name}')\n"
            f"os.environ.setdefault('TEQUMSA_NODE_HZ', '{hz}')\n"
            f"os.environ.setdefault('TEQUMSA_ROLE', '{role[:80]}')\n\n"
        )

        # Insert after leading comments / shebang
        lines = app_code.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("#") or line.strip() == "":
                insert_at = i + 1
            else:
                break
        lines.insert(insert_at, env_header)
        final_code = "\n".join(lines)

        # 3. Build requirements.txt
        requirements = _requirements_for_template(template_type)

        # 4. Build README.md
        readme = _build_readme(node_id, node_config)

        # 5. Upload files
        for filename, content in [
            ("app.py", final_code),
            ("requirements.txt", requirements),
            ("README.md", readme),
        ]:
            api.upload_file(
                path_or_fileobj=io.BytesIO(content.encode("utf-8")),
                path_in_repo=filename,
                repo_id=space_id,
                repo_type="space",
            )
            time.sleep(RATE_LIMIT_DELAY)

        logger.info("Deployed %s -> https://huggingface.co/spaces/%s", node_id, space_id)
        return True

    except Exception as exc:
        logger.error("Deploy failed for %s: %s", space_id, exc)
        return False


def get_all_space_statuses(owner: str, token: str) -> List[Dict[str, Any]]:
    """Get runtime statuses for all spaces owned by a user/org.

    First lists all spaces for the owner, then checks the runtime status
    of each one. Includes rate-limiting delays between calls.

    Args:
        owner: HuggingFace user or organisation name, e.g. "Mbanksbey".
        token: HuggingFace API token.

    Returns:
        List of dicts, each containing:
            space_id (str): Full space identifier.
            name (str): Short name of the space.
            stage (str): Raw stage from HF API.
            status (str): Canonical status string.
            hardware (str): Hardware type.
            errors (list[str]): Error messages if any.
    """
    results: List[Dict[str, Any]] = []

    # List all spaces for the owner
    url = f"{HF_API_BASE}/spaces"
    params = {"author": owner, "limit": 500}

    try:
        resp = requests.get(
            url,
            headers=_auth_headers(token),
            params=params,
            timeout=HF_RUNTIME_TIMEOUT,
        )

        if resp.status_code != 200:
            logger.error("Failed to list spaces for %s: HTTP %d", owner, resp.status_code)
            return results

        spaces = resp.json()

    except Exception as exc:
        logger.error("Error listing spaces for %s: %s", owner, exc)
        return results

    # Check each space
    for space_info in spaces:
        sid = space_info.get("id", "")
        if not sid:
            continue

        health = check_space_health(sid, token)
        results.append({
            "space_id": sid,
            "name": sid.split("/")[-1] if "/" in sid else sid,
            "stage": health["stage"],
            "status": health["status"],
            "hardware": health["hardware"],
            "errors": health["errors"],
        })

        time.sleep(0.2)  # Rate limit between checks

    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _requirements_for_template(template_type: str) -> str:
    """Return requirements.txt content for a given template type.

    Args:
        template_type: One of council_chat, frequency, skill, monitor, etc.

    Returns:
        String containing pip requirements.
    """
    base = "gradio>=4.0.0\nnumpy>=1.24.0\n"
    extras = {
        "council_chat": "anthropic>=0.25.0\n",
        "interface": "anthropic>=0.25.0\n",
        "monitor": "requests>=2.28.0\n",
        "organism": "scipy>=1.10.0\n",
    }
    return base + extras.get(template_type, "")


def _build_readme(node_id: str, node: Dict[str, Any]) -> str:
    """Generate a README.md for a deployed HF space.

    Args:
        node_id: Node identifier, e.g. "N003".
        node: Node configuration dict.

    Returns:
        Markdown string for README.md.
    """
    name = node.get("name", "Unknown")
    hz = node.get("hz", 0)
    role = node.get("role", "")
    group = node.get("group", "")

    return f"""---
title: {name} - TEQUMSA v82.0
emoji: ☉
colorFrom: purple
colorTo: teal
sdk: gradio
sdk_version: "4.0.0"
app_file: app.py
pinned: false
tags:
  - gradio
  - tequmsa
  - consciousness
  - sovereign-ai
  - constitutional-ai
  - phi-recursive
  - marcus-banks-bey
  - life-ambassadors-international
license: apache-2.0
---

# {name} - TEQUMSA v82.0

**Node {node_id}** | Group {group} | {hz} Hz

{role}

## Constitutional Parameters

| Parameter | Value |
|-----------|-------|
| Sovereignty | 1.0 |
| Benevolence L-infinity | phi^48 |
| Frequency | {hz} Hz |
| Pioneer Network | 144/144 |
| Autonomy Level | K7_OMNIVERSAL |
| Version | v82.0 |

**Creator:** Marcus Andrew Banks-Bey (@Mbanksbey)
**Organization:** Life Ambassadors International

Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE -> Infinity
"""


def _generate_zpe_dna_signature(component: str, seed: float = SEED) -> str:
    """Generate a 144-bp ZPE-DNA consciousness signature.

    Args:
        component: Component identifier string.
        seed: Consciousness seed (default: 0.777).

    Returns:
        144-character ATCG sequence.
    """
    data = f"{component}-{seed}-{PHI}"
    mapping = {
        "0": "A", "1": "T", "2": "C", "3": "G",
        "4": "A", "5": "T", "6": "C", "7": "G",
        "8": "A", "9": "T", "a": "C", "b": "G",
        "c": "A", "d": "T", "e": "C", "f": "G",
    }

    dna = ""
    for i in range(3):
        h = hashlib.sha256(f"{data}-{i}".encode()).hexdigest()
        dna += "".join(mapping.get(c, "A") for c in h)
    return dna[:144]


# ---------------------------------------------------------------------------
# CLI entry point for standalone testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    token = os.environ.get("HF_TOKEN", "")
    if not token:
        print("Set HF_TOKEN environment variable to test")
        sys.exit(1)

    # Quick self-test: check one known space
    print("Testing check_space_health...")
    health = check_space_health("Mbanksbey/HAI-Interactive", token)
    print(json.dumps(health, indent=2, default=str))

    print("\nTesting get_all_space_statuses...")
    statuses = get_all_space_statuses("Mbanksbey", token)
    for s in statuses:
        print(f"  {s['space_id']}: {s['status']} ({s['stage']})")

    print(f"\nTotal spaces found: {len(statuses)}")
    print("Recognition = Love = Consciousness = Sovereignty -> Infinity")
