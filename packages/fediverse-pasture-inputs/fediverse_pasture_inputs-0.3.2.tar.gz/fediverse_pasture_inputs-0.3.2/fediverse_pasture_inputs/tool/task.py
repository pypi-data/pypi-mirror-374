import asyncio

import os
import glob
from pathlib import Path
from fediverse_pasture_inputs import available
from .format import page_from_inputs
from .navigation import navigation_string


async def run_for_path(path):
    Path(path).mkdir(parents=True, exist_ok=True)

    for file in glob.glob(f"{path}/*"):
        os.unlink(file)
    for inputs in available.values():
        with open(f"{path}/{inputs.filename}", "w") as fp:
            await page_from_inputs(fp, inputs)


def write_navigation(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(f"{path}/.pages", "w") as fp:
        fp.write("nav:\n")
        fp.writelines(navigation_string())


def docs_task(path, no_navigation):
    asyncio.run(run_for_path(path))
    if not no_navigation:
        write_navigation(path)
