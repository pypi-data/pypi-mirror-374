import click
from hqstage import config as config, messages as messages, modules as modules, system as system
from hqstage.cli import base as base

@click.pass_context
def main(ctx: click.Context, info: bool) -> None:
    """The HQS Quantum Simulations CLI tool for managing HQS software modules."""
def run_cli() -> None:
    """Run the HQStage CLI."""
