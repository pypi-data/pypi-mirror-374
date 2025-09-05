import sys
from pathlib import Path

CWD = Path(__file__).parent
sys.path.insert(0, str(CWD.parent / 'src' / 'easy_config_hub'))