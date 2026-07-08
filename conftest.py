"""Root conftest — ensures project root is on sys.path for all pytest runs."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
