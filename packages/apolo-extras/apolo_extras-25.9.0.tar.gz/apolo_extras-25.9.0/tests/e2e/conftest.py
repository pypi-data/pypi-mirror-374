import asyncio
import logging
import os
import re
import subprocess
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from typing import (
    AsyncIterator,
    Callable,
    ContextManager,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Union,
)

import apolo_sdk  # NOTE: don't use async test functions (issue #129)
import pytest
from tenacity import retry, stop_after_attempt, stop_after_delay

from apolo_extras.common import APOLO_EXTRAS_IMAGE
from apolo_extras.config import _build_registy_auth
from apolo_extras.image_builder import KANIKO_AUTH_PREFIX


DISK_PREFIX = "<DISK_PREFIX>"
TEMPDIR_PREFIX = "<TEMPDIR_PREFIX>"

UUID4_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
DISK_ID_PATTERN = rf"disk-{UUID4_PATTERN}"
DISK_ID_REGEX = re.compile(DISK_ID_PATTERN)

logger = logging.getLogger(__name__)

TEST_DATA_COPY_LOCAL_TO_LOCAL = True
TEST_DATA_COPY_CLOUD_TO_LOCAL = True
TEST_DATA_COPY_LOCAL_TO_CLOUD = True
TEST_DATA_COPY_CLOUD_TO_PLATFORM = True
TEST_DATA_COPY_PLATFORM_TO_CLOUD = True

CLOUD_SOURCE_PREFIXES: Dict[str, str] = {
    # "gs": "gs://mlops-ci-e2e-tests/assets/data", # disabled, since we cannot easily test it via internal network   # noqa: E501
    "s3": "s3://apolo-extras-test-assets/assets/data",
    # "azure+https": "azure+https://neuromlops.blob.core.windows.net/cookiecutter-e2e/assets/data",  # noqa: E501
    "http": "https://apolo-extras-test-assets.s3.us-east-1.amazonaws.com/assets/data",
    "https": "https://apolo-extras-test-assets.s3.us-east-1.amazonaws.com/assets/data",
}

CLOUD_DESTINATION_PREFIXES: Dict[str, str] = {
    # "gs": "gs://mlops-ci-e2e-tests/data_cp",
    "s3": "s3://apolo-extras-test-assets/assets/data_cp",
    # "azure+https": "azure+https://neuromlops.blob.core.windows.net/cookiecutter-e2e/data_cp",  # noqa: E501
    "http": "https://apolo-extras-test-assets.s3.us-east-1.amazonaws.com/assets/data",
    "https": "https://apolo-extras-test-assets.s3.us-east-1.amazonaws.com/assets/data",
}

PLATFORM_SOURCE_PREFIXES: Dict[str, str] = {
    # apolo mkdir -p storage:e2e/assets/data
    # apolo cp -rT tests/assets/data storage:e2e/assets/data
    "storage": "storage:e2e/assets/data",
    # apolo disk create --name extras-e2e --timeout-unused 1000d 100M
    # apolo run -v storage:e2e/assets/data:/storage -v disk:extras-e2e:/disk alpine -- sh -c "mkdir -p /disk/assets && cp -rT /storage /disk/assets/data" # noqa: E501
    "disk": f"disk:extras-e2e/assets/data",
}

PLATFORM_DESTINATION_PREFIXES: Dict[str, str] = {
    # apolo storage mkdir storage:e2e/data_cp
    "storage": "storage:e2e/data_cp",
    "disk": f"{DISK_PREFIX}/data_cp",
}

SRC_CLUSTER_ENV_VAR = "APOLO_CLUSTER"
DST_CLUSTER_ENV_VAR = "APOLO_CLUSTER_SECONDARY"


class CLIRunner(Protocol):
    def __call__(
        self, args: List[str], enable_retry: bool = False
    ) -> "CompletedProcess[str]": ...


def get_tested_archive_types() -> List[str]:
    """Get tested archive types

    If PYTEST_DATA_COPY_ARCHIVE_TYPES is set,
    returns its value, split on `,`.
    Otherwise, returns default archive types.

    See `apolo_extras.data.archive.ArchiveType.get_extension_mapping()`
    for supported extensions.
    """
    env = os.environ.get("PYTEST_DATA_COPY_ARCHIVE_TYPES")
    if env:
        return env.split(",")
    else:
        return [".tar.gz"]


@dataclass
class Secret:
    name: str
    value: str

    def __repr__(self) -> str:
        return f"Secret(name='{self.name}', value='HIDDEN!'"


def generate_random_secret(name_prefix: str = "secret") -> Secret:
    return Secret(
        name=f"{name_prefix}-{uuid.uuid4().hex[:8]}",
        value=str(uuid.uuid4()),
    )


@pytest.fixture
def temp_random_secret(cli_runner: CLIRunner) -> Iterator[Secret]:
    secret = generate_random_secret()
    try:
        yield secret
    finally:
        cli_runner(["apolo", "secret", "rm", secret.name])


def gen_random_file(location: Union[str, Path], name: Optional[str] = None) -> Path:
    location = Path(location)
    location.mkdir(parents=True, exist_ok=True)
    name = name or f"file-{uuid.uuid4().hex[:8]}.txt"
    file = location / name
    file.write_text(str(uuid.uuid4()))
    return file


@pytest.fixture(scope="session", autouse=True)
def print_apolo_extras_image() -> None:
    logger.warning(f"Using apolo-extras image: '{APOLO_EXTRAS_IMAGE}'")


async def _async_get_bare_client() -> apolo_sdk.Client:
    """Return uninitialized apolo client."""
    return await apolo_sdk.get()


@pytest.fixture
def _apolo_client() -> Iterator[apolo_sdk.Client]:
    # Note: because of issue #129 we can't use async methods of the client,
    # therefore this fixture is private
    client = asyncio.run(_async_get_bare_client())
    try:
        yield asyncio.run(client.__aenter__())
    finally:
        asyncio.run(client.__aexit__())  # it doesn't use arguments


@pytest.fixture
def current_user(_apolo_client: apolo_sdk.Client) -> str:
    return _apolo_client.username


@pytest.fixture
def switch_cluster(
    _apolo_client: apolo_sdk.Client,
) -> Callable[[str], ContextManager[None]]:
    @contextmanager
    def _f(cluster: str) -> Iterator[None]:
        orig_cluster = _apolo_client.config.cluster_name
        try:
            logger.info(f"Temporary cluster switch: {orig_cluster} -> {cluster}")
            asyncio.run(_apolo_client.config.switch_cluster(cluster))
            yield
        finally:
            logger.info(f"Switch back cluster: {cluster} -> {orig_cluster}")
            try:
                asyncio.run(_apolo_client.config.switch_cluster(orig_cluster))
            except Exception as e:
                logger.error(
                    f"Could not switch back to cluster '{orig_cluster}': {e}. "
                    f"Please run manually: 'apolo config switch-cluster {orig_cluster}'"
                )

    return _f


@pytest.fixture
async def dockerhub_auth_secret() -> AsyncIterator[Secret]:
    async with apolo_sdk.get() as apolo_client:
        secret_name = f"{KANIKO_AUTH_PREFIX}_{uuid.uuid4().hex}"
        auth_data = _build_registy_auth(
            # Why not v2: https://github.com/GoogleContainerTools/kaniko/pull/1209
            registry_uri="https://index.docker.io/v1/",
            username=os.environ["DOCKER_CI_USERNAME"],
            password=os.environ["DOCKER_CI_TOKEN"],
        )
        secret = Secret(secret_name, auth_data)
        try:
            await apolo_client.secrets.add(secret_name, auth_data.encode())
            logger.debug(f"Created test secret: {secret}")
            yield secret
        finally:
            await apolo_client.secrets.rm(secret_name)


@pytest.fixture
def project_dir() -> Iterator[Path]:
    with TemporaryDirectory() as cwd_str:
        old_cwd = Path.cwd()
        cwd = Path(cwd_str)
        os.chdir(cwd)
        try:
            yield cwd
        finally:
            os.chdir(old_cwd)


@retry(stop=stop_after_attempt(3) | stop_after_delay(5 * 10))
def run_cli(args: List[str]) -> "CompletedProcess[str]":
    proc = subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode:
        logger.warning(f"Got '{proc.returncode}' for '{' '.join(args)}'")
    logger.info(f"stdout of {args}: {proc.stdout}")
    if proc.stderr:
        logger.warning(f"stderr of {args}: {proc.stderr}")
    return proc


@pytest.fixture
def cli_runner(project_dir: Path) -> CLIRunner:
    return run_cli  # type: ignore


@pytest.fixture
def args_data_cp_from_cloud(cli_runner: CLIRunner) -> Callable[..., List[str]]:
    def _f(
        bucket: str,
        src: str,
        dst: str,
        extract: bool,
        compress: bool,
        use_temp_dir: bool,
    ) -> List[str]:
        args = ["apolo-extras", "data", "cp", src, dst]
        if (
            src.startswith("storage:")
            or dst.startswith("storage:")
            or src.startswith("disk:")
            or dst.startswith("disk:")
        ):
            if bucket.startswith("gs://"):
                args.extend(
                    [
                        "-v",
                        "secret:apolo-extras-gcp:/gcp-creds.txt",
                        "-e",
                        "GOOGLE_APPLICATION_CREDENTIALS=/gcp-creds.txt",
                    ]
                )
            elif bucket.startswith("s3://"):
                args.extend(
                    [
                        "-v",
                        "secret:apolo-extras-aws:/aws-creds.txt",
                        "-e",
                        "AWS_CONFIG_FILE=/aws-creds.txt",
                    ]
                )
            elif bucket.startswith("azure+https://"):
                args.extend(
                    [
                        "-e",
                        "AZURE_SAS_TOKEN=secret:azure_sas_token",
                    ]
                )
            elif bucket.startswith("https://") or bucket.startswith("http://"):
                # No additional arguments required
                pass
            else:
                raise NotImplementedError(bucket)
        if extract:
            args.append("-x")
        if compress:
            args.append("-c")
        if use_temp_dir:
            args.append("-t")
        logger.info("args = %s", args)
        return args

    return _f


@pytest.fixture
def disk(cli_runner: CLIRunner) -> Iterator[str]:
    """Provide temporary disk, which will be removed upon test end

    WARNING: when used with pytest-xdist,
    disk will be created one per each worker!
    """
    # Create disk
    res = cli_runner(["apolo", "disk", "create", "100M"])
    assert res.returncode == 0, res
    disk_id = None
    try:
        output_lines = "\n".join(res.stdout.splitlines())

        search = DISK_ID_REGEX.search(output_lines)
        if search:
            disk_id = search.group()
        else:
            raise Exception("Can't find disk ID in apolo output: \n" + res.stdout)
        logger.info(f"Created disk {disk_id}")
        yield f"disk:{disk_id}"

    finally:
        logger.info(f"Removing disk {disk_id}")
        try:
            # Delete disk
            if disk_id is not None:
                res = cli_runner(["apolo", "disk", "rm", disk_id])
                assert res.returncode == 0, res
        except BaseException as e:
            logger.warning(f"Finalization error: {e}")


@pytest.fixture(scope="session")
def src_cluster() -> Iterator[str]:
    res = os.environ.get(SRC_CLUSTER_ENV_VAR)
    if not res:
        raise ValueError(f"'{SRC_CLUSTER_ENV_VAR}' env var is missing")
    yield res


@pytest.fixture(scope="session")
def dst_cluster() -> Iterator[str]:
    res = os.environ.get(DST_CLUSTER_ENV_VAR)
    if not res:
        pytest.skip(
            f"{DST_CLUSTER_ENV_VAR} env var"
            " indicating destination cluster is missing, skipping test"
        )
    yield res


@pytest.fixture
def smallest_preset(_apolo_client: apolo_sdk.Client) -> str:
    presets = list(_apolo_client.config.presets.items())
    presets = list(filter(lambda x: x[0].lower() != "vast-ai", presets))
    presets.sort(key=lambda x: x[1].cpu)
    return presets[0][0]


@pytest.fixture
def build_preset(smallest_preset: str) -> str:
    env_preset = os.environ.get("APOLO_EXTRAS_PRESET")
    if env_preset:
        return env_preset
    else:
        return smallest_preset
