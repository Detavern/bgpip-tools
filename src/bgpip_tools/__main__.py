#!/usr/bin/env python3

import os
import json

import click

from .config import DATA_DIR, DIST_DIR, ROOT_LOGGER, load_config

DEFAULT_ASNS_FILENAME = 'asns.json'
DEFAULT_CIDRS_DIR = 'cidrs'

logger = ROOT_LOGGER.getChild('cli')


@click.group()
@click.option('-c', '--config-dir', type=str, default=None, help="configuration directory")
@click.pass_context
def cli(ctx, config_dir):
    ctx.ensure_object(dict)
    if config_dir and os.path.isdir(config_dir) is False:
        raise click.ClickException(f'could not find configuration directory at {config_dir}')
    load_config(config_dir)


@cli.group('config')
def config_group():
    """Configuration related commands"""


@config_group.command('print')
@click.option('-i', '--indent', type=int, default=2, help="output strings/file indentations if available")
def config_print(indent):
    """Print current configurations"""
    from .config import get_config_dict
    config = get_config_dict()
    print(json.dumps(config, indent=indent))


@cli.group('asn')
def asn_group():
    """ASN related commands"""


@asn_group.command('prepare', hidden=True)
@click.pass_context
def asn_prepare(ctx, **kwargs):
    from .data import prepare_data_asn
    os.makedirs(DATA_DIR, exist_ok=True)
    prepare_data_asn()


@asn_group.command('stat')
@click.pass_context
def asn_stat(ctx):
    from .data import stat_data_asn

    ctx.forward(asn_prepare)
    stat_data_asn()


@asn_group.command('generate')
@click.pass_context
@click.option('-i', '--indent', type=int, default=2, help="output strings/file indentations if available")
@click.option('-o', '--output-dir', type=str, default=DIST_DIR, help="output directory")
@click.option('-f', '--filename', type=str, default=DEFAULT_ASNS_FILENAME, help="output filename")
def asn_generate(ctx, indent, output_dir, filename):
    """Generate ASN mapping from asn_filters"""
    from .asn import load_asns_by_config

    ctx.forward(asn_prepare)
    os.makedirs(output_dir, exist_ok=True)

    asns = load_asns_by_config()

    fp = os.path.join(output_dir, filename)
    with open(fp, 'w') as f:
        logger.getChild('asn').info(f'{filename} generated at {fp}')
        json.dump(asns, f, indent=indent)
    return asns


@cli.group('bgp')
def bgp_group():
    """BGP related commands"""


@bgp_group.command('prepare', hidden=True)
@click.pass_context
def bgp_prepare(ctx, **kwargs):
    from .data import prepare_data_bgp

    # load asns
    if kwargs.get('use_dist'):
        asns_fp = os.path.join(DIST_DIR, DEFAULT_ASNS_FILENAME)
        if os.path.isfile(asns_fp):
            with open(asns_fp) as f:
                ctx.obj['asns'] = json.load(f)
    if 'asns' not in ctx.obj:
        kw = {}
        if 'output_dir' in ctx.params:
            kw['output_dir'] = ctx.params['output_dir']
        ctx.obj['asns'] = ctx.invoke(asn_generate, **kw)

    # load bgp info
    if 'bgp' not in ctx.obj:
        ctx.obj['bgp'] = prepare_data_bgp()


@bgp_group.command('info')
@click.option('-i', '--indent', type=int, default=2, help="output strings/file indentations if available")
@click.pass_context
def bgp_info(ctx, indent):
    """Query remote BGP information"""
    from .data import get_bgp_info
    print(json.dumps(get_bgp_info(), indent=indent))


@bgp_group.command('generate')
@click.option('-u', '--use-dist', is_flag=True, default=False)
@click.option('-o', '--output-dir', type=str, default=DIST_DIR, help="output directory")
@click.option('-d', '--dry-run', is_flag=True, help="dry run")
@click.option('-n4', '--no-ipv4', is_flag=True, help="skip ipv4 cidrs generate")
@click.option('-n6', '--no-ipv6', is_flag=True, help="skip ipv6 cidrs generate")
@click.pass_context
def bgp_generate(ctx, use_dist, output_dir, dry_run, no_ipv4, no_ipv6):
    """Generate CIDRs from ASN mapping and BGP data"""
    from .bgp import load_cidr_by_asns

    ctx.forward(bgp_prepare)
    os.makedirs(output_dir, exist_ok=True)

    cidr_map = {}
    if not no_ipv4:
        v4_output_dir = os.path.join(output_dir, DEFAULT_CIDRS_DIR, 'v4')
        os.makedirs(v4_output_dir, exist_ok=True)
        cidr_map['ipv4'] = load_cidr_by_asns(
            ctx.obj['bgp']['ipv4'], ctx.obj['asns'], v4=True, dry_run=dry_run)
        for k, cidrs in cidr_map['ipv4'].items():
            fp = os.path.join(v4_output_dir, f'{k}.txt')
            with open(fp, 'w') as f:
                for cidr in cidrs:
                    f.write(f'{cidr}\n')
                logger.getChild('bgp').info(f'v4/{k} generated at {fp}')

    if not no_ipv6:
        v6_output_dir = os.path.join(output_dir, DEFAULT_CIDRS_DIR, 'v6')
        os.makedirs(v6_output_dir, exist_ok=True)
        cidr_map['ipv6'] = load_cidr_by_asns(
            ctx.obj['bgp']['ipv6'], ctx.obj['asns'], v6=True, dry_run=dry_run)
        for k, cidrs in cidr_map['ipv6'].items():
            fp = os.path.join(v6_output_dir, f'{k}.txt')
            with open(fp, 'w') as f:
                for cidr in cidrs:
                    f.write(f'{cidr}\n')
                logger.getChild('bgp').info(f'v6/{k} generated at {fp}')

    return cidr_map


if __name__ == "__main__":
    cli()
