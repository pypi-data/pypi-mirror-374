from __future__ import annotations

import click

from runchain.chain import Chain, list_chains


class ChainType(click.ParamType):
    """
    Click parameter type for Chain objects.
    """
    name = "chain"
    
    def __init__(self, required: bool = True):
        self.required = required
    
    def convert(self, value, param, ctx):
        if value is None:
            if self.required:
                self.fail("Chain name is required", param, ctx)
            return None
        return Chain(value)


@click.group()
@click.version_option()
def cli() -> None:
    """
    runchain: manage and run chains of scripts
    """
    pass


@cli.command()
@click.argument("chain", type=ChainType(required=False), required=False)
def list(chain: Chain | None) -> None:
    """
    List all chains or scripts within a specific chain.
    """
    if chain is None:
        chains = list_chains()
        if not chains:
            click.echo("No chains found.")
            return
        click.echo("Chains found:")
        for c in chains:
            click.echo(c)
    else:
        scripts = chain.list()
        if not scripts:
            click.echo(f"No scripts found in chain '{chain.name}'.")
            return
        click.echo(f"Scripts in chain {chain.name}:")
        for script in scripts:
            click.echo(script)


@cli.command()
@click.argument("chain", type=ChainType())
@click.argument("script")
@click.argument("target", required=False)
def add(chain: Chain, script: str, target: str | None) -> None:
    """
    Add a script to a chain.
    """
    filename = chain.add_file(script, target)
    click.echo(f"Added {filename} to chain '{chain.name}'")


@cli.command()
@click.argument("chain", type=ChainType())
@click.argument("script", required=False)
@click.argument("target", required=False)
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def remove(chain: Chain, script: str | None, target: str | None, force: bool) -> None:
    """
    Remove a script from a chain, or remove an entire chain.
    """
    if script is None:
        # Remove entire chain
        if not force and chain.exists():
            scripts = chain.list()
            if scripts and not click.confirm(f"Chain '{chain.name}' contains {len(scripts)} script(s). Remove anyway?"):
                return
        
        chain.destroy()
        click.echo(f"Removed chain '{chain.name}'")
    else:
        # Remove script from chain
        chain.remove(script, target)
        click.echo(f"Removed script from chain '{chain.name}'")


@cli.command()
@click.argument("chain", type=ChainType())
@click.argument("schedule")
def cron(chain: Chain, schedule: str) -> None:
    """
    Register a chain to run on a cron schedule using crondir.
    """
    chain.cron(schedule)
    click.echo(f"Scheduled chain '{chain.name}' with crondir")


@cli.command()
@click.argument("chain", type=ChainType())
def run(chain: Chain) -> None:
    """
    Execute all scripts in a chain in alphabetical order.
    """
    success = chain.run()
    if not success:
        raise click.Abort()


def invoke() -> None:
    """
    Entry point for the CLI.
    """
    cli()
