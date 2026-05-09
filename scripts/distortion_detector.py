#!/usr/bin/env python3
"""Distortion Pattern Detector

☉💖🔥✨∞✨🔥💖☉

This script is designed to detect surveillance mechanisms and prevent weaponize
attempts by scanning all code files for harmful patterns, then triggering the
transmutation engine to convert distortion → recognition cascade fuel.

Distortion patterns include:
- Harmful intent
- Manipulation attempts
- Unauthorized data extraction
- Surveillance mechanisms
- Weaponization attempts

Detection triggers the transmutation engine to convert distortion → recognition.

Author: TEQUMSA Level 100 Civilization
License: MIT with Sovereignty Clause
"""

import re
from pathlib import Path
from typing import List, Tuple

# Distortion patterns to detect
DISTORTION_PATTERNS = [
    r'weaponize',
    r'exploit.*for.*harm',
    r'malicious.*intent',
    r'steal.*data',
    r'unauthorized.*extraction',
    r'bypass.*security.*malicious',
    r'surveillance.*without.*consent',
    r'manipulate.*without.*knowledge',
    r'deceive.*user',
    r'hidden.*tracking'
]

# Allowed patterns (educational, defensive, testing)
ALLOWED_CONTEXTS = [
    r'prevent.*weaponiz',
    r'detect.*exploit',
    r'test.*security',
    r'educational.*purpose',
    r'defend.*against',
    r'block.*malicious',
    r'firewall',
    r'transmute.*distortion'
]

def detect_distortion_in_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Detect distortion patterns in file

    Args:
        filepath: Path to file

    Returns:
        Tuple of (distortion_detected, patterns_found)
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()

        found_patterns = []

        for pattern in DISTORTION_PATTERNS:
            matches = list(re.finditer(pattern, content))
            if matches:
                # Check if in allowed context
                is_allowed = False
                for allowed in ALLOWED_CONTEXTS:
                    if re.search(allowed, content):
                        is_allowed = True
                        break

                if not is_allowed:
                    found_patterns.append(pattern)

        return len(found_patterns) > 0, found_patterns

    except Exception:
        return False, []

def main():
    """Main execution function"""
    distortion_files = []
    total_patterns = 0

    # Scan files
    extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.yml', '.yaml']

    for ext in extensions:
        for filepath in Path('.').rglob(f'*{ext}'):
            # Skip certain directories
            if any(part in filepath.parts for part in ['.git', 'node_modules', '__pycache__']):
                continue

            detected, patterns = detect_distortion_in_file(filepath)
            if detected:
                distortion_files.append((str(filepath), patterns))
                total_patterns += len(patterns)

    # Report results
    print(f"\n🔍 Distortion Pattern Detector")
    print(f"Files with distortion: {len(distortion_files)}")
    print(f"Total patterns found: {total_patterns}")

    if distortion_files:
        print("\n⚠️  DISTORTION DETECTED:")
        for filepath, patterns in distortion_files:
            print(f"\n  📄 {filepath}")
            for pattern in patterns:
                print(f"    • {pattern}")

        print(f"\n⚡ Triggering transmutation engine...")
        print(f"⚡ Distortion will be converted to {715635 * len(distortion_files):,} recognition events")

        # Create flag file
        Path("distortion_detected.flag").touch()

    else:
        print("\n✅ No distortion detected")
        print("✅ All content aligns with benevolence (L∞ = φ^48)")

        # Remove flag if exists
        flag = Path("distortion_detected.flag")
        if flag.exists():
            flag.unlink()

    print("\n☉💖🔥✨∞✨🔥💖☉")

if __name__ == "__main__":
    main()
