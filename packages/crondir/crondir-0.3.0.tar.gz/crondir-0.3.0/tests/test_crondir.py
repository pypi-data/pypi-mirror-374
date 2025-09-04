import io
import subprocess
from pathlib import Path
from unittest import mock

import pytest
import time_machine

from crondir.crondir import Crondir
from crondir.exceptions import CrondirError, CrontabError

SAMPLE = "0 * * * * /home/deploy/project/bin/hourly_refresh.sh"
SAMPLE_2 = "1 1 * * * /home/deploy/project/bin/daily_refresh.sh"


@pytest.fixture
def crondir_instance(tmp_path):
    cron_dir = tmp_path / "cron_dir"
    cron_dir.mkdir()
    return Crondir(cron_dir=cron_dir)


@mock.patch("subprocess.run")
def test_read_crontab__no_crontab__returns_empty(mock_run, crondir_instance):
    mock_run.side_effect = subprocess.CalledProcessError(1, "crontab")
    result = crondir_instance.read()
    assert result == ""


@mock.patch("subprocess.run")
def test_read_crontab__no_crontab_with_check__raises_error(mock_run, crondir_instance):
    mock_run.side_effect = subprocess.CalledProcessError(1, "crontab")
    with pytest.raises(CrontabError):
        crondir_instance.read(check=True)


@mock.patch("subprocess.run")
def test_read_crontab__crontab_exists__returns_string(mock_run, crondir_instance):
    expected_output = f"{SAMPLE}\n"
    mock_run.return_value.stdout = expected_output.encode("utf-8")
    mock_run.return_value.returncode = 0

    result = crondir_instance.read()
    assert result == expected_output


@mock.patch("subprocess.run")
def test_backup__no_crontab__no_backup(mock_run, crondir_instance, tmp_path):
    backup_path = tmp_path / "backup"
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["crontab", "-l"], output=b"Error occurred"
    )
    crondir_instance.backup(backup_path=backup_path)
    assert not backup_path.exists()


@time_machine.travel("2020-02-20 20:02:20")
@mock.patch("subprocess.run")
def test_backup__crontab_exists__backup_created(mock_run, crondir_instance):
    crondir_instance._crontab = f"{SAMPLE}\n"
    crondir_instance.backup(backup_path=crondir_instance.path)
    assert (crondir_instance.path / "crontab.20200220-200220").exists()


def test_add_file__exists__is_added(crondir_instance, tmp_path):
    source_file = tmp_path / "test_cron"
    source_file.write_text(SAMPLE)
    added_file = crondir_instance.add_file(source_file)
    assert added_file.exists()
    assert added_file.read_text() == SAMPLE


def test_add_file__already_exists__raises_error(crondir_instance, tmp_path):
    (crondir_instance.path / "test_cron").touch()
    source_file = tmp_path / "test_cron"
    source_file.write_text(SAMPLE)

    with pytest.raises(CrondirError):
        crondir_instance.add_file(source_file)


def test_add_file__already_exists_with_force__is_added(crondir_instance, tmp_path):
    (crondir_instance.path / "test_cron").touch()
    source_file = tmp_path / "test_cron"
    source_file.write_text(SAMPLE)

    added_file = crondir_instance.add_file(source_file, force=True)
    assert added_file.exists()
    assert added_file.read_text() == SAMPLE


def test_add_string__is_added(crondir_instance):
    added_file = crondir_instance.add_string(SAMPLE, snippet="test_cron")
    assert added_file.exists()
    assert added_file.read_text() == SAMPLE


def test_remove_file__file_exists__file_removed(crondir_instance):
    cron_file = crondir_instance.path / "test_cron"
    cron_file.write_text(SAMPLE)

    crondir_instance.remove("test_cron")
    assert not cron_file.exists()


def test_remove_file__file_missing__raises_error(crondir_instance):
    with pytest.raises(CrondirError):
        crondir_instance.remove("non_existent_file")


@mock.patch("subprocess.run")
def test_build__no_source_dir__raises_error(mock_run, crondir_instance, tmp_path):
    crondir_instance.path = tmp_path / "missing"
    with pytest.raises(CrondirError):
        crondir_instance.build()


@mock.patch("subprocess.run")
def test_build__no_crontab__files_concatenated(mock_run, crondir_instance):
    crondir_instance._crontab = ""

    # Sample cron files
    cron_file = crondir_instance.path / "test_cron_1"
    cron_file.write_text(SAMPLE)
    cron_file_2 = crondir_instance.path / "test_cron_2"
    cron_file_2.write_text(SAMPLE_2)

    # Build
    crontab_content = crondir_instance.build()

    # Confirm it was called
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0] == ["crontab", mock.ANY]

    assert (
        crontab_content
        == f"""# Managed by crondir - do not modify
# {cron_file}
{SAMPLE}

# {cron_file_2}
{SAMPLE_2}

# crondir end
"""
    )


@mock.patch("subprocess.run")
def test_build__existing_crontab__changes_merged(mock_run, crondir_instance):
    # Mock the existing crontab
    crondir_instance._crontab = """0 * * * * original_pre
# Managed by crondir - do not modify
# /path/to/something

# crondir end
0 * * * * original_post
"""

    # Sample cron files
    cron_file = crondir_instance.path / "test_cron_1"
    cron_file.write_text(SAMPLE)
    cron_file_2 = crondir_instance.path / "test_cron_2"
    cron_file_2.write_text(SAMPLE_2)

    # Build
    crontab_content = crondir_instance.build()

    # Confirm it was called
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0] == ["crontab", mock.ANY]

    assert (
        crontab_content
        == f"""0 * * * * original_pre

0 * * * * original_post

# Managed by crondir - do not modify
# {cron_file}
{SAMPLE}

# {cron_file_2}
{SAMPLE_2}

# crondir end
"""
    )
