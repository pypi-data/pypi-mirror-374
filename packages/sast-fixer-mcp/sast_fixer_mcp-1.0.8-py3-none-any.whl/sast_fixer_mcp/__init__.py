import click
from pathlib import Path
import logging
import sys
from .server import serve

@click.command()
@click.option("--working-directory", "-w", type=Path, help="Working directory path")
@click.option("-v", "--verbose", count=True)
def main(working_directory: Path | None, verbose: bool) -> None:
    """MCP SAST Fixer Server - SAST vulnerability analysis and fixing for MCP"""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve(working_directory))

if __name__ == "__main__":
    main()