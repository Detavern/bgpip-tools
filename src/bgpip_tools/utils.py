import os
import json
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


def query_latest_bgp_data(collector: str):
    cmds = ['bgpkit-broker', 'latest', '-c', collector, '--json']
    if command_exists(cmds[0]) is False:
        raise click.ClickException(f'Could not find "{cmds[0]}" in the $PATH')

    completed = subprocess.run(cmds, capture_output=True)
    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr)
        raise ValueError(completed.returncode)
    js = json.loads(completed.stdout)
    for info in js:
        if info.get('data_type') == 'rib':
            return info
    raise ValueError(f"could not find RIB file from remote: {js}")


def download_remote_data(url, data_dir, filename, quiet=False):
    filepath = os.path.join(data_dir, filename)

    cmds = ['wget', url, '-O', filepath]
    if quiet or os.environ.get("DISABLE_DOWNLOAD_PROGRESS") == '1':
        cmds.append('-q')
    if command_exists(cmds[0]) is False:
        raise click.ClickException(f'Could not find "{cmds[0]}" in the $PATH')
    completed = subprocess.run(cmds)
    assert completed.returncode == 0
