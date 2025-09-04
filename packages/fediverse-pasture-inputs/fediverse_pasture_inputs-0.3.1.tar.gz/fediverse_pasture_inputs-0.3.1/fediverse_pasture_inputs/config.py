from glob import glob
from urllib.parse import urljoin

resource_base_path = "http://pasture-one-actor/assets/"
"""Base path to resources"""

used_resources: set[str] = set()
"""List of used resources"""


def resource_path(asset: str) -> str:
    """Returns the path to the asset

    ```pycon
    >>> resource_path("cow_emoji.png")
    'http://pasture-one-actor/assets/cow_emoji.png'

    ```
    """

    used_resources.add(asset)

    return urljoin(resource_base_path, asset)


def check_resources(path_to_resources: str = "./assets/"):
    paths = glob(f"{path_to_resources}/*")
    paths_as_set = {x.removeprefix(path_to_resources) for x in paths}
    diff = used_resources - paths_as_set

    if len(diff) > 0:
        raise Exception("Unknown resource used: " + ", ".join(diff))
