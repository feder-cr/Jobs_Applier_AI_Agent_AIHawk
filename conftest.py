import sys
from pathlib import Path

# The tests import main.py, which lives at the repository root. pytest puts the
# test file's own directory on sys.path, not this one, so it goes on explicitly.
sys.path.insert(0, str(Path(__file__).parent))
