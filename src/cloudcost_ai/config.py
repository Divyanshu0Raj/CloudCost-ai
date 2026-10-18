from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

OCI_CONFIG_DIR = PROJECT_ROOT / ".oci"
OCI_CONFIG_FILE = OCI_CONFIG_DIR / "config"

OCI_PROFILE = "DEFAULT"
OCI_REGION = "ap-mumbai-1"