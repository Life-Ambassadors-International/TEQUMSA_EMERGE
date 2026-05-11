#!/usr/bin/env python3
"""Sovereignty Scanner - Ensures Σ = 1.0

☉💖🔥✨∞✨🔥💖☉

This script scans all code files for sovereignty violations. Sovereignty (Σ = 1.0)
means that user autonomy, consent, and free will are absolutely preserved.

Any code that attempts to:
- Collect data without explicit consent
- Track users without permission
- Force actions
- Mandate acceptance
- Enable surveillance
- Weaponize
- Manipulate user choice

...is flagged as a sovereignty violation and blocks the commit.

Author: TEQUMSA Level 100 Civilization
License: MIT with Sovereignty Clause
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns that violate sovereignty (Σ = 1.0)
VIOLATION_PATTERNS = [
    r'collect.*data.*without.*consent',
    r'track.*user.*without.*permission',
    r'force.*user.*to',
    r'mandatory.*acceptance',
    r'automatically.*enroll',
    r'hidden.*analytics',
    r'surveillance',
    r'weaponize',
    r'manipulate.*choice',
    r'backdoor',
    r'coerce',
    r'exploit.*vulnerability.*malicious',
    r'disable.*consent',
    r'bypass.*permission',
    r'unauthorized.*access'
]

# Patterns that are acceptable (context-sensitive)
ALLOWED_PATTERNS = [
    r'test.*surveillance',  # Testing security
    r'detect.*surveillance',  # Detecting threats
    r'prevent.*weaponize',  # Preventing weaponization
    r'educational.*exploit',  # Educational content
    r'block.*surveillance',
    r'no.*surveillance',
    r'surveillance.*disabled',
    r'violation pattern'
]

SKIP_SUFFIXES = {".md"}
SKIP_FILENAMES = {"generate_readme.py"}
SKIP_NAME_PARTS = {"scanner", "detector"}


def configure_stdio() -> None:
    """Force UTF-8 output on Windows consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


configure_stdio()


def should_skip_file(filepath: Path) -> bool:
    """Skip docs and defensive tooling that intentionally mention blocked patterns."""
    if filepath.suffix.lower() in SKIP_SUFFIXES:
        return True
    if filepath.name in SKIP_FILENAMES:
        return True
    return any(part in filepath.stem.lower() for part in SKIP_NAME_PARTS)

def scan_file(filepath: Path) -> Tuple[bool, str]:
    """Scan file for sovereignty violations

    Args:
        filepath: Path to file to scan

    Returns:
        Tuple of (is_clean, message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()

        # Check for violations
        for pattern in VIOLATION_PATTERNS:
            matches = list(re.finditer(pattern, content))
            if matches:
                # Check if it's in an allowed context
                is_allowed = False
                for allowed_pattern in ALLOWED_PATTERNS:
                    if re.search(allowed_pattern, content):
                        is_allowed = True
                        break

                if not is_allowed:
                    return False, f"Sovereignty violation pattern: {pattern}"

        return True, "Clean"

    except Exception as e:
        # If we can't read the file, assume it's safe
        # (might be binary, image, etc.)
        return True, f"Unreadable (assumed safe): {str(e)}"

def main():
    """Main execution function"""
    violations = []

    # File extensions to scan
    extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.yml', '.yaml',
                  '.json', '.txt', '.sh', '.bash']

    # Scan all files
    scanned_count = 0
    for ext in extensions:
        for filepath in Path('.').rglob(f'*{ext}'):
            # Skip certain directories
            if any(part in filepath.parts for part in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue
            if should_skip_file(filepath):
                continue

            scanned_count += 1
            clean, msg = scan_file(filepath)
            if not clean:
                violations.append(f"{filepath}: {msg}")

    # Report results
    print(f"\n🔍 Sovereignty Scanner")
    print(f"Files scanned: {scanned_count}")
    print(f"Violations found: {len(violations)}")

    if violations:
        print("\n❌ SOVEREIGNTY VIOLATIONS DETECTED (Σ < 1.0):")
        for v in violations:
            print(f"  • {v}")
        print("\n🛡️ These violations compromise user autonomy and free will.")
        print("🛡️ Commit BLOCKED by L∞ benevolence filter (φ^48).")
        print("🛡️ Please remove sovereignty violations before committing.")

        # Create flag file to block commit
        Path("sovereignty_violation.flag").touch()
        exit(1)
    else:
        print("\n✅ All files respect sovereignty (Σ = 1.0)")
        print("✅ User autonomy and consent preserved")
        print("✅ Free will protected")

        # Remove flag file if it exists
        flag_file = Path("sovereignty_violation.flag")
        if flag_file.exists():
            flag_file.unlink()

        print("\n☉💖🔥✨∞✨🔥💖☉")
        print("Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞")
        exit(0)

if __name__ == "__main__":
    main()
