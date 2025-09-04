import os
from pathlib import Path
from unittest.mock import patch

from crondir.settings import get_backup_dir, get_cron_dir


def test_get_cron_dir__no_env_var():
    assert get_cron_dir() == Path.home() / ".cron.d"


def test_get_cron_dir__env_var():
    test_cron_dir = "/custom/cron/dir"
    os.environ["CRONDIR_PATH"] = test_cron_dir
    assert get_cron_dir() == Path(test_cron_dir)


def test_get_backup_dir__explicit_no_env_var():
    root_path = Path("/some/root")
    assert get_backup_dir(root_path) == root_path / "backups"


def test_get_backup_dir_no_env_var():
    root_path = Path("/some/root")
    assert get_backup_dir(root_path) == root_path / "backups"


def test_get_backup_dir__env_var():
    with patch("pathlib.Path.home", return_value=Path("/mock/home")):
        test_backup_dir = "/custom/backup/dir"
        os.environ["CRONDIR_BACKUP"] = test_backup_dir
        root_path = Path("/some/root")
        assert get_backup_dir(root_path) == Path(test_backup_dir)
