"""Restore tasks.json from tasks.seed.json so the demo starts clean."""

import shutil
from pathlib import Path

here = Path(__file__).resolve().parent
shutil.copyfile(here / "tasks.seed.json", here / "tasks.json")
print("Demo data reset: tasks.json restored from tasks.seed.json")
