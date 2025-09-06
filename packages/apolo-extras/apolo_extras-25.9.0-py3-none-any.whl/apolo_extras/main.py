import logging
from pathlib import Path
from typing import Any, MutableMapping

import toml

from .cli import main
from .config import save_registry_auth  # noqa
from .data import data_cp, data_transfer  # noqa
from .image import image_build, image_transfer  # noqa
from .k8s import generate_k8s_registry_secret, generate_k8s_secret  # noqa


logger = logging.getLogger(__name__)


@main.command("init-aliases")
def init_aliases() -> None:
    """
    Create apolo CLI aliases for apolo-extras functionality.
    """
    # TODO: support patching the global ~/.neuro/user.toml
    toml_path = Path.cwd() / ".neuro.toml"
    config: MutableMapping[str, Any] = {}
    if toml_path.exists():
        with toml_path.open("r") as f:
            config = toml.load(f)
    config.setdefault("alias", {})
    config["alias"]["image-build"] = {
        "exec": "apolo-extras image build",
        "options": [
            "-f, --file=PATH  path to the Dockerfile within CONTEXT",
            "--build-arg=LIST  build arguments for Docker",
            "--build-tag=LIST  tag(s) for image builder job.",
            "-e, --env=LIST  environment variables for container",
            "-v, --volume=LIST  list of volumes for container",
            "-s, --preset=STR  specify  preset for builder container",
            "-F, --force-overwrite  enforce destination image overwrite",
        ],
        "args": "CONTEXT_PATH IMAGE_URI",
        "help": (
            "Build docker image on the platform. "
            "Hit `apolo-extras image build --help` for more info."
        ),
    }
    config["alias"]["local-build"] = {
        "exec": "apolo-extras image local-build",
        "options": [
            "-f, --file=PATH  path to the Dockerfile within CONTEXT",
            "--build-arg=LIST  build arguments for Docker",
            "-F, --force-overwrite  enforce destination image overwrite",
        ],
        "args": "CONTEXT_PATH IMAGE_URI",
        "help": (
            "Build docker image using local Docker daemon. "
            "Hit `apolo-extras image local-build --help` for more info."
        ),
    }
    config["alias"]["image-transfer"] = {
        "exec": "apolo-extras image transfer",
        "args": "SOURCE DESTINATION",
        "options": [
            "-F, --force-overwrite  enforce destination image overwrite",
        ],
        "help": (
            "Transfer images between the cluster within the platform. "
            "Hit `apolo-extras image transfer --help` for more info."
        ),
    }
    config["alias"]["data-transfer"] = {
        "exec": "apolo-extras data transfer",
        "args": "SOURCE DESTINATION",
    }
    config["alias"]["data-cp"] = {
        "exec": "apolo-extras data cp",
        "options": [
            "-c, --compress Compress source files",
            "-x, --extract Extract downloaded files",
            "-e, --env environment variables for container",
            "-v, --volume list of volumes for container",
            "-t, --use-temp-dir store intermediate data in TMP directory",
            "-s, --preset=NAME  specify  preset for copy container",
            "-l, --life_span=MINUTES  specify life span for copy container",
        ],
        "args": "SOURCE DESTINATION",
    }
    with toml_path.open("w") as f:
        toml.dump(config, f)
    logger.info(f"Added aliases to {toml_path}")
