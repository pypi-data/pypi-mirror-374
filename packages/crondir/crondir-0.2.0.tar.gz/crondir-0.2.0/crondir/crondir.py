import datetime
import shutil
import subprocess
import tempfile
from pathlib import Path

from .exceptions import CrondirError, CrontabError
from .settings import get_backup_dir, get_cron_dir

START_MARKER = "# Managed by crondir - do not modify"
END_MARKER = "# crondir end"


class Crondir:
    path: Path
    _crontab: str | None = None

    def __init__(self, cron_dir: Path | str | None = None):
        """
        Crondir manager

        Args:
            cron_dir (Path | str | None): The path of the crondir source dir. If `None`,
                use the env var CRONDIR_PATH, or the default source dir.
        """
        self.path = Path(cron_dir) if cron_dir else get_cron_dir()

    def read(self, refresh: bool = False, check: bool = False) -> str:
        """
        Read the crontab

        Args:
            refresh (bool): If True, ignore any cached value
            check (bool): If True, raise a CrontabFail error, otherwise return empty

        Returns:
            str: Current contents of the crontab
        """
        if self._crontab is not None and not refresh:
            return self._crontab

        try:
            out = subprocess.run(
                ["crontab", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            if check:
                msg = e.stderr.decode("utf-8") if e.stderr else "Unknown error"
                raise CrontabError(f"Failed to read crontab: {msg}")
            self._crontab = ""
        else:
            self._crontab = out.stdout.decode("utf-8")
        return self._crontab

    def backup(self, backup_path: Path | str | None):
        """
        Backup the current crontab to the backup dir

        Does not backup if the crontab is empty

        Args:
            backup_path (Path | str | None): The path of the backup dir. If `None`, use
                the env var CRONDIR_BACKUP, or the default backup dir.
        """
        crontab = self.read()
        if not crontab:
            return

        # Get backup path
        if backup_path is None:
            backup_path = get_backup_dir(self.path)
        else:
            backup_path = Path(backup_path)

        # Ensure if exists
        if not backup_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)

        # Dump crontab into backup file
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = backup_path / f"crontab.{timestamp}"
        backup_file.write_text(crontab)

    def build(self) -> str:
        """
        Build the crontab from the source dir

        Returns:

            str: The new crontab
        """
        if not self.path.exists():
            raise CrondirError(f"Source dir {self.path} does not exist")

        # Find placeholder in crontab
        crontab = self.read()
        crontab_pre, _, _ = crontab.partition(START_MARKER)
        _, _, crontab_post = crontab.partition(END_MARKER)

        # Build crontab content
        content = []
        if crontab_pre:
            content.append(f"{crontab_pre.strip()}\n")
        if crontab_post:
            content.append(f"{crontab_post.strip()}\n")

        content.append(START_MARKER)

        for cron_file in sorted(self.path.iterdir()):
            if cron_file.is_file() and not cron_file.name.startswith("."):
                content.append(f"# {cron_file}")
                with open(cron_file, "r") as f:
                    content.extend([f.read().strip(), ""])

        content.extend([END_MARKER, ""])

        # Write the content to a temporary file and load it in
        new_crontab = "\n".join(content)
        with tempfile.NamedTemporaryFile(mode="w") as crontab_file:
            crontab_file.write(new_crontab)
            crontab_file.flush()
            try:
                subprocess.run(
                    ["crontab", crontab_file.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                raise CrontabError(
                    f"Failed to load crontab: {e.stderr.decode('utf-8')}"
                )
        return new_crontab

    def add_file(
        self,
        source_file: Path | str,
        *,
        cron_name: str | None = None,
        force: bool = False,
    ) -> Path:
        """
        Add a cron snippet file to the cron dir

        Args:
            source_file (Path | str): The path of the cron definition to add.
            force (bool): If False, raise an error if the destination file exists.
            cron_name (str | None): The name for the file in the cron_dir. If not set,
                use the current filename.
        """
        source_file = Path(source_file)
        if not source_file.is_file():
            raise CrondirError(f"File {source_file} not found")

        # Find cron dir and destination file path
        if not cron_name:
            cron_name = source_file.name
        dest_file = self.path / cron_name
        if dest_file.exists() and not force:
            raise CrondirError(f"{dest_file} already exists. Use --force to overwrite.")
        if dest_file.name.startswith("."):
            raise CrondirError(f"{dest_file} cannot start with a period.")

        # Create cron dir - only place this happens
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

        shutil.copy(source_file, dest_file)
        return dest_file

    def add_string(
        self,
        *contents: str,
        cron_name: str | None,
        force: bool = False,
    ) -> Path:
        """
        Add a cron snippet string to the cron dir under the specified name
        """
        with tempfile.NamedTemporaryFile(mode="w") as snippet:
            snippet.write("\n".join(contents))
            snippet.flush()
            return self.add_file(snippet.name, force=force, cron_name=cron_name)

    def remove(
        self,
        cron_name: str,
        *,
        force: bool = False,
    ) -> bool:
        """
        Remove a cron file from the cron dir

        Returns:

            bool: True if a snippet was removed, False if it didn't exist
        """
        target_file = self.path / cron_name
        if not target_file.exists():
            if not force:
                raise CrondirError(
                    f"{target_file} does not exist. Use --force to ignore."
                )
            return False

        target_file.unlink()
        return True

    def list(self) -> list[Path]:
        """
        List the snippets in the cron dir
        """
        return [
            cron_file
            for cron_file in sorted(self.path.iterdir())
            if cron_file.is_file() and not cron_file.name.startswith(".")
        ]
