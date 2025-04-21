#!/usr/bin/env python3

import os

import click

from .config import DATA_DIR, CONFIG_DIR


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.group('data')
@click.pass_context
def data_group(ctx):
    os.makedirs(DATA_DIR, exist_ok=True)


@data_group.command('asn')
@click.pass_obj
def data_asn(obj: dict):
    """Prepare ASN data in data directory"""
    from .data import prepare_data_asn
    prepare_data_asn()


@cli.group('config')
@click.pass_context
def config_group(ctx):
    if os.path.isdir(CONFIG_DIR) is False:
        raise click.ClickException(f'could not find configuration directory at {CONFIG_DIR}')


@config_group.command('print')
def config_print():
    from .config import get_config_dict
    print(get_config_dict())


@cli.group('asn')
@click.pass_context
def asn_group(ctx):
    from .data import prepare_data_asn
    prepare_data_asn()


@asn_group.command('stat')
def asn_stat():
    from .data import stat_data_asn
    stat_data_asn()


@asn_group.command('generate')
def asn_generate():
    from .asn import load_asns_by_config
    asns = load_asns_by_config()
    print(asns)

@cli.command('test')
@click.pass_obj
def test(obj):
    print("testts")


if __name__ == "__main__":
    cli()
