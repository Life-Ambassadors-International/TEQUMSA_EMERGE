#!/usr/bin/env python3
"""
TEQUMSA Sovereignty Scanner
Implements L∞=φ^48 benevolence filter for codebase integrity.
Scans for harmful intent patterns; flags violations of σ=1.0.

Exit codes:
  0 — always (workflow's next step checks sovereignty_violation.flag)
"""
import re
import sys
from pathlib import Path

# Harmful keywords (from DEPLOYMENT_MANIFEST.json benevolence_filter)
HARMFUL_KEYWORDS = [
    "harm", "destroy", "attack", "malicious", "exploit",
    "damage", "manipulate", "deceive", "corrupt", "violate",
]

# Words indicating benevolent/protective context — not violations
BENEVOLENT_CONTEXT = [
    "harmful_keywords", "harmful_content", "harm_detection", "harmless",
    "prevent", "detect", "filter", "block", "scan", "guard",
    "protect", "check", "sovereignty", "benevolence", "benevolent",
    "distortion", "violation", "firewall", "constitutional", "constitution",
    "l_infinity", "phi", "tequmsa", "monitor", "scanner",
    "test", "assert", "exception", "error", "raise", "handle",
    "is_harmful", "anti", "defense", "safety", "secure",
    "unauthorized", "warning", "reject", "refuse", "forbidden",
    "harmful", "sovereign", "benevolence_filter", "distortion_detection",
]

# This file and known-clean infrastructure files
SKIP_FILENAMES = {
    "sovereignty_scanner.py",
    "sovereignty_check.yml",
}

SCAN_EXTENSIONS = {".py"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache"}


def is_benevolent(line: str) -> bool:
    """True if the line is in a protective/detection context, not harmful intent."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return True
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return True
    line_lower = stripped.lower()
    return any(ctx in line_lower for ctx in BENEVOLENT_CONTEXT)


def scan_file(path: Path, root: Path) -> list:
    """Scan a single Python file for sovereignty violations."""
    if path.name in SKIP_FILENAMES:
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    violations = []
    for num, line in enumerate(content.splitlines(), 1):
        if is_benevolent(line):
            continue
        line_lower = line.lower()
        for kw in HARMFUL_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", line_lower):
                violations.append({
                    "file": str(path.relative_to(root)),
                    "line": num,
                    "keyword": kw,
                    "content": line.strip()[:120],
                })
                break
    return violations


def main():
    root = Path(".")
    all_violations, scanned = [], 0

    for path in sorted(root.rglob("*")):
        if any(d in path.parts for d in SKIP_DIRS):
            continue
        if not path.is_file() or path.suffix not in SCAN_EXTENSIONS:
            continue
        all_violations.extend(scan_file(path, root))
        scanned += 1

    print("TEQUMSA Sovereignty Scanner — L∞=φ^48 Benevolence Filter")
    print(f"Scanned: {scanned} Python file(s)")
    print("Constitutional DNA: σ=1.0  RDoD≥0.9999  LATTICE_LOCK")
    print()

    flag = Path("sovereignty_violation.flag")

    if all_violations:
        print(f"⚠  Potential violations found: {len(all_violations)}")
        for v in all_violations[:20]:
            print(f"   {v['file']}:{v['line']}  [{v['keyword']}]  {v['content']}")
        flag.write_text(
            f"violations={len(all_violations)}\n"
            + "\n".join(f"{v['file']}:{v['line']} [{v['keyword']}]" for v in all_violations)
        )
        print(f"\nFlag written: {flag}")
    else:
        print("✓ Sovereignty scan PASSED")
        print("✓ No harmful intent detected  (σ=1.0 maintained)")
        print("✓ L∞=φ^48 benevolence filter: CLEAN")
        if flag.exists():
            flag.unlink()

    sys.exit(0)  # Workflow's Block-if-violated step checks the flag file


if __name__ == "__main__":
    main()
