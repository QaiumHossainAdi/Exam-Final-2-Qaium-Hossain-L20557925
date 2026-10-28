"""Config loading and unit conversion helpers."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config" / "castcheck.yaml"

PSI_PER_MPA = 145.038
LBYD3_PER_KGM3 = 1.68555  # 1 kg/m3 = 1.68555 lb/yd3


def load_config(path=None):
    with open(path or DEFAULT_CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def mpa_to_psi(x):
    return x * PSI_PER_MPA


def psi_to_mpa(x):
    return x / PSI_PER_MPA


def kgm3_to_lbyd3(x):
    return x * LBYD3_PER_KGM3


def lbyd3_to_kgm3(x):
    return x / LBYD3_PER_KGM3
