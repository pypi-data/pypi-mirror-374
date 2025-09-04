import click

from .crondir import Crondir


@click.group()
def cli():
    """
    crondir: manage your cron jobs
    """
    pass


@cli.command()
@click.option(
    "--cron-dir",
    type=str,
    default=None,
    help="Override the cron dir",
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Do not create a backup before merging",
)
@click.option(
    "--backup-path",
    type=str,
    default=None,
    help="Path to store backups",
)
def build(cron_dir, no_backup, backup_path):
    """
    Build the crontab from the cron dir
    """
    crondir = Crondir(cron_dir)
    if not no_backup:
        crondir.backup(backup_path)
    crondir.build()


@cli.command()
@click.argument(
    "source_file",
    type=click.Path(exists=True),
)
@click.argument(
    "cron_name",
    type=str,
    default=None,
    required=False,
)
@click.option(
    "--force",
    is_flag=True,
    help="Force add the file, overwriting if it exists.",
)
@click.option(
    "--cron-dir",
    type=str,
    default=None,
    help="Override the cron dir",
)
def add(source_file, cron_name, force, cron_dir):
    """
    Add a cron snippet to the crondir dir
    """
    cron_file = Crondir(cron_dir).add_file(
        source_file, force=force, cron_name=cron_name
    )
    click.echo(f"Added {cron_file.name}. Rebuild with crontab build.")


@cli.command()
@click.argument(
    "cron_name",
    type=str,
)
@click.option(
    "--force",
    is_flag=True,
    help="Force remove the file, ignoring if it does not exist.",
)
@click.option(
    "--cron-dir",
    type=str,
    default=None,
    help="Override the cron dir",
)
def remove(cron_name, force, cron_dir):
    """
    Remove a cron snippet from the crondir dir
    """
    removed = Crondir(cron_dir).remove(cron_name, force=force)
    if removed:
        click.echo(f"Removed {cron_name}. Rebuild with crontab build.")
    else:
        click.echo(f"{cron_name} not found.")


@cli.command()
@click.option(
    "--cron-dir",
    type=str,
    default=None,
    help="Override the cron dir",
)
def list(cron_dir):
    """
    List all current cron snippets
    """
    for snippet in Crondir(cron_dir).list():
        click.echo(snippet.name)
    else:
        click.echo("No snippets installed")


def invoke():
    cli(obj={})
