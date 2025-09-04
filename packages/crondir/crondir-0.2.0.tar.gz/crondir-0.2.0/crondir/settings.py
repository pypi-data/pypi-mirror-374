import os
from pathlib import Path

CRON_DIR = Path.home() / ".cron.d"
BACKUP_DIR_NAME = "backups"


def get_cron_dir() -> Path:
    # Check for env var
    if env := os.getenv("CRONDIR_PATH"):
        return Path(env)

    return CRON_DIR


def get_backup_dir(root: Path) -> Path:
    if env := os.getenv("CRONDIR_BACKUP"):
        return Path(env)

    return root / BACKUP_DIR_NAME
