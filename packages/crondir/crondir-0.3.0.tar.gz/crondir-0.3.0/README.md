# crondir

[![PyPI](https://img.shields.io/pypi/v/crondir.svg)](https://pypi.org/project/crondir/)
[![Documentation](https://readthedocs.org/projects/crondir/badge/?version=latest)](https://crondir.readthedocs.io/en/latest/)
[![Tests](https://github.com/radiac/crondir/actions/workflows/ci.yml/badge.svg)](https://github.com/radiac/crondir/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/radiac/crondir/branch/main/graph/badge.svg?token=BCNM45T6GI)](https://codecov.io/gh/radiac/crondir)

Manage your user crontab with snippets in a cron.d directory in your home.

Simplifies the automated management of cron tasks in the user space. Snippets are
concatenated from your cron.d into the crontab.

- Store and manage crontab snippets in separate files
- Does not interfere with existing crontab entries
- Backs up crontab each time it builds
- Everything configurable

## Usage

A crontab snippet is a file containing lines to go in a crontab.

To install:

```bash
pip install crondir
```

Add a cron snippet:

```bash
crondir add path/to/snippet_name
```

Remove a cron snippet:

```bash
crondir remove snippet_name
```

List installed cron snippets:

```bash
crondir list
```

Build the crontab from current definitions:

```bash
crondir build
```

Or you may find it easier to skip the install step and run it using
[uv](https://docs.astral.sh/uv/).

```bash
uvx crondir add path/to/snippet_name
uvx crondir remove path/to/snippet_name
uvx crondir list
uvx crondir build
```

By default, crondir stores crontab snippets in `~/.cron.d/`, and creates backups
in `~/.cron.d/backups/`.

For full command line options, see [command documentation](https://crondir.readthedocs.io/en/latest/commands.html)

## Example

Lets say we're deploying a project with hourly and daily cron tasks, and will be running
it from a `deploy` user. Our project is at `/home/deploy/project/`

Create a snippet file in our project, `cron_tasks`, containing the lines to add to the
crontab:

```
0 * * * * /home/deploy/project/bin/hourly_refresh.sh
1 0 * * * /home/deploy/project/bin/daily_refresh.sh
```

To add this snippet, run:

```bash
cd ~
uvx crondir add project/cron_task project_tasks
uvx crondir build
```

This will:

- create the dir `~/.cron.d/`
- copy `project/cron_task` into `~/.cron.d/` as `~/.cron.d/project_tasks`
- rebuild the crontab to include the lines from `~/.cron.d/project_tasks`

If we want to remove the snippet, we can run:

```bash
cd ~
uvx crondir remove project_tasks
uvx crondir build
```

This will

- remove the file `~/.cron.d/project_tasks`
- concatenate all the files in `~/.cron.d`
- add them to the crontab under any existing unmanaged entries
