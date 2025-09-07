import asyncio
import click
import zipfile


from pathlib import Path
from fediverse_pasture_inputs import available

from .tool.format import add_samples_to_zip
from .tool.task import docs_task, write_navigation


@click.group()
def main():
    """Tool for helping with creating the documentation for the
    fediverse-pasture-inputs"""
    ...


@main.command()
@click.option(
    "--path",
    default="docs/inputs",
    help="Path of the directory the documentation pages are to be deposited",
)
@click.option("--no_navigation", is_flag=True, default=False)
@click.option(
    "--watch",
    is_flag=True,
    default=False,
    help="Watch for changes in the fediverse_pasture_inputs directory",
)
def docs(path, no_navigation, watch):
    """Creates a documentation page for each input"""

    if watch:
        from watchfiles import run_process

        run_process(
            "fediverse_pasture_inputs", target=docs_task, args=(path, no_navigation)
        )
    else:
        docs_task(path, no_navigation)


@main.command()
@click.option(
    "--path",
    default="docs/inputs",
    help="Path of the directory the documentation pages are to be deposited",
)
def navigation(path):
    """Writes the .pages file for the inputs used to generate the documentation.
    Usually runs automatically when generating the documentation."""
    write_navigation(path)


@main.command()
@click.option(
    "--path",
    default="docs/assets",
    help="Path of the directory the zip file is created at",
)
def zip_file(path):
    """Creates a zip file containing the the generated ActivityPub objects
    and activities"""
    Path(path).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(f"{path}/samples.zip", "w") as zipcontainer:
        for inputs in available.values():
            asyncio.run(add_samples_to_zip(zipcontainer, inputs))


if __name__ == "__main__":
    main()
