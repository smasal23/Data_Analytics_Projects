# Initializes the project environment by adding the project root to sys.path so shared modules can be
# imported in notebooks and scripts.

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))