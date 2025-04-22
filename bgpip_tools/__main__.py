#!/usr/bin/env python3

import os
import json

import click

from .config import DATA_DIR, CONFIG_DIR, DIST_DIR


DEFAULT_ASNS_FILENAME = 'asns.json'
DEFAULT_CIDRS_DIR = 'cidrs'


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.group('config')
def config_group():
    """Configuration related commands"""
    if os.path.isdir(CONFIG_DIR) is False:
        raise click.ClickException(f'could not find configuration directory at {CONFIG_DIR}')


@config_group.command('print')
def config_print():
    from .config import get_config_dict
    print(get_config_dict())


@cli.group('asn')
def asn_group():
    """ASN related commands"""


@asn_group.command('prepare', hidden=True)
@click.pass_context
def asn_prepare(ctx, **kwargs):
    from .data import prepare_data_asn
    prepare_data_asn()


@asn_group.command('stat')
@click.pass_context
def asn_stat(ctx):
    from .data import stat_data_asn

    ctx.forward(asn_prepare)
    stat_data_asn()


@asn_group.command('generate')
@click.pass_context
@click.option('-i', '--indent', type=int, default=2)
@click.option('-o', '--output', type=str, default=None)
def asn_generate(ctx, indent, output):
    from .asn import load_asns_by_config

    ctx.forward(asn_prepare)
    if output is None:
        os.makedirs(DIST_DIR, exist_ok=True)
        output = os.path.join(DIST_DIR, DEFAULT_ASNS_FILENAME)
    asns = load_asns_by_config()

    with open(output, 'w') as f:
        print(f'DIST[asns] generated at {output}')
        json.dump(asns, f, indent=indent)
    return asns


@cli.group('bgp')
def bgp_group():
    """BGP related commands"""


@bgp_group.command('prepare', hidden=True)
@click.pass_context
def bgp_prepare(ctx, **kwargs):
    from .data import get_bgp_info

    # load asns
    if kwargs.get('use_dist'):
        asns_fp = os.path.join(DIST_DIR, DEFAULT_ASNS_FILENAME)
        if os.path.isfile(asns_fp):
            with open(asns_fp) as f:
                ctx.obj['asns'] = json.load(f)
    if 'asns' not in ctx.obj:
        ctx.obj['asns'] = ctx.invoke(asn_generate)

    # load bgp info
    if 'bgp' not in ctx.obj:
        ctx.obj['bgp'] = get_bgp_info()


@bgp_group.command('generate')
@click.option('-u', '--use-dist', is_flag=True, default=False)
@click.option('-o', '--output-dir', type=str, default=None)
@click.option('-d', '--dry-run', is_flag=True, help='dry run')
@click.option('-n4', '--no-ipv4', is_flag=True, help='skip ipv4 cidrs generate')
@click.option('-n6', '--no-ipv6', is_flag=True, help='skip ipv6 cidrs generate')
@click.pass_context
def bgp_generate(ctx, use_dist, output_dir, dry_run, no_ipv4, no_ipv6):
    from .bgp import load_cidr_by_asns

    ctx.forward(bgp_prepare)
    if output_dir is None:
        output_dir = os.path.join(DIST_DIR, DEFAULT_CIDRS_DIR)
    os.makedirs(output_dir, exist_ok=True)

    cidr_map = {}
    if not no_ipv4:
        v4_output_dir = os.path.join(output_dir, 'v4')
        os.makedirs(v4_output_dir, exist_ok=True)
        cidr_map['ipv4'] = load_cidr_by_asns(ctx.obj['bgp']['ipv4'], ctx.obj['asns'], dry_run)
        for k, cidrs in cidr_map['ipv4'].items():
            fp = os.path.join(v4_output_dir, f'{k}.txt')
            with open(fp, 'w') as f:
                for cidr in cidrs:
                    f.write(f'{cidr}\n')
                print(f'DIST[ipv4][{k}] generated at {fp}')

    if not no_ipv6:
        v6_output_dir = os.path.join(output_dir, 'v6')
        os.makedirs(v6_output_dir, exist_ok=True)
        cidr_map['ipv6'] = load_cidr_by_asns(ctx.obj['bgp']['ipv6'], ctx.obj['asns'], dry_run)
        for k, cidrs in cidr_map['ipv6'].items():
            fp = os.path.join(v6_output_dir, f'{k}.txt')
            with open(fp, 'w') as f:
                for cidr in cidrs:
                    f.write(f'{cidr}\n')
                print(f'DIST[ipv6][{k}] generated at {fp}')

    return cidr_map


if __name__ == "__main__":
    cli()
