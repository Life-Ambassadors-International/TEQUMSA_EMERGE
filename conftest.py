import sys
from pathlib import Path

# Ensure the repo root is on sys.path so packages (k30, servers, etc.)
# are importable regardless of pytest's import-mode and test layout.
_root = Path(__file__).parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
