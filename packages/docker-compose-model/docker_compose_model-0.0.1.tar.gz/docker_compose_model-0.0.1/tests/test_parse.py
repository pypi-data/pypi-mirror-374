import pytest
import os
import glob
from dcm import parse_compose_files


@pytest.mark.parametrize(
    "relative_dir,expected_services,expected_volumes,expected_secrets,expected_networks",
    [("samples/multi-files-01/*.yml", 3, 2, 2, 2)],
)
def test_parse_compose_files(
    relative_dir: str,
    expected_services: int,
    expected_volumes: int,
    expected_secrets: int,
    expected_networks: int,
) -> None:
    sample_dir = os.path.join(os.path.dirname(__file__), relative_dir)
    files = list(glob.glob(pathname=sample_dir))
    print("[DEBUG] Found files:", files)
    compose = parse_compose_files(*files)
    assert len(compose.services) == expected_services
    assert len(compose.volumes) == expected_volumes
    assert len(compose.secrets) == expected_secrets
    assert len(compose.networks) == expected_networks
