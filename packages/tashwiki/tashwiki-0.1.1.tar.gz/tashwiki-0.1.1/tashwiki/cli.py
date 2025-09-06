import logging
from pathlib import Path

import click
from livereload import Server

from tashwiki import __version__
from tashwiki.config import Config
from tashwiki.builder import Builder

logger = logging.getLogger()
def_conf = Path("config.cfg")


@click.group("tashwiki")
@click.option(
    "--config",
    type=click.Path(),
    help="Path to the configuration file."
)
@click.pass_context
def cli(ctx, config):
    print(f"TashWiki v{__version__}")
    if not config and def_conf.exists():
        config = def_conf
    if config:
        conf = Config.from_file(config)
    else:
        conf = Config.default()
    ctx.obj = {
        "config": conf,
    }


@cli.command()
@click.pass_context
def build(ctx):
    """Build the website."""
    config = ctx.obj["config"]
    Builder(config).build()


@cli.command()
@click.option("--reload", is_flag=True, help="Enable automatic reloading.")
@click.option("--port", type=int, default=8080, help="Webserver port.")
@click.pass_context
def serve(ctx, reload, port):
    """Run development web server"""
    config = ctx.obj["config"]

    def rebuild():
        Builder(config).build()

    server = Server()
    if reload:
        rebuild()
        server.watch(config.site_source_dir, func=rebuild)
    server.serve(port=port, root=config.site_output_dir)


def main():
    cli()
