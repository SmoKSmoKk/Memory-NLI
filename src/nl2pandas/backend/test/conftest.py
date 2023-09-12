import sys
from pathlib import Path

path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(path))
