"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """pytest-static."""


if __name__ == "__main__":
    main(prog_name="pytest-static")  # pragma: no cover
