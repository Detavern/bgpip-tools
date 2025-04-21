import os
import click
import shutil
import subprocess


def command_exists(cmd) -> bool:
    return shutil.which(cmd) is not None


def download_asn_data(data_dir, filename):
    filepath = os.path.join(data_dir, filename)

    cmds = ['asninfo', filepath]
    if command_exists(cmds[0]) is False:
        raise click.ClickException(f'Could not find "{cmds[0]}" in the $PATH')

    completed = subprocess.run(cmds)
    assert completed.returncode == 0
    return
