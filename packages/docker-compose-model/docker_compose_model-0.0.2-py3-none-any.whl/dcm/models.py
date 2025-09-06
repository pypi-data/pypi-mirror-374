from enum import Enum
from typing import Any, Optional, TypeVar, Union

from . import spec


def parse_list_of_dict_of_tuples(
    list_or_dict: Optional[
        Union[dict[str, Any], list[Any], spec.ListOrDict, spec.ListOrDict1]
    ],
) -> dict[str, Any]:
    if isinstance(list_or_dict, dict):
        return list_or_dict
    if isinstance(list_or_dict, list):
        res: dict[str, Any] = {}
        for e in list_or_dict:
            if "=" in str(e):
                x = str(e).split("=", maxsplit=1)
                res[x[0]] = x[1]
        return res
    if isinstance(list_or_dict, (spec.ListOrDict, spec.ListOrDict1)):
        return parse_list_of_dict_of_tuples(list_or_dict.root)
    assert list_or_dict is None
    return {}


class Protocol(str, Enum):
    # pylint: disable=invalid-name
    tcp = "tcp"
    udp = "udp"
    any = "any"

    def __repr__(self) -> str:
        return self.name


class AppProtocol(str, Enum):
    # pylint: disable=invalid-name
    rest = "REST"
    mqtt = "MQTT"
    wbsock = "WebSocket"
    http = "http"
    https = "https"
    na = "NA"

    def __repr__(self) -> str:
        return self.name


class Port:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        source_file: str,
        host: str,
        source_port: str,
        container_port: str,
        protocol: Protocol = Protocol.any,
        app_protocol: AppProtocol = AppProtocol.na,
    ):
        self.host = host
        self.source_port = source_port
        self.container_port = container_port
        self.protocol = protocol
        self.app_protocol = app_protocol
        self.source_files: list[str] = [source_file]


class VolumeType(str, Enum):
    # pylint: disable=invalid-name
    volume = "volume"
    bind = "bind"
    tmpfs = "tmpfs"
    npipe = "npipe"


class Volume:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        source_file: str,
        source: str,
        target: str,
        v_type: VolumeType = VolumeType.volume,
        access_mode: str = "rw",
    ):
        self.source = source
        self.target = target
        self.v_type = v_type
        self.access_mode = access_mode
        self.source_files: list[str] = [source_file]


class Device:
    def __init__(
        self,
        source_file: str,
        host_path: str,
        container_path: str,
        cgroup_permissions: Optional[str] = None,
    ):
        self.host_path = host_path
        self.container_path = container_path
        self.cgroup_permissions = cgroup_permissions
        self.source_files: list[str] = [source_file]


class Extends:
    def __init__(self, service_name: str, from_file: Optional[str] = None):
        self.service_name = service_name
        self.from_file = from_file


T = TypeVar("T")


def opt_to_arr(opt: Optional[list[T]]) -> list[T]:
    if opt is None:
        return []
    return opt


def opt_to_dict(opt: Optional[dict[str, T]]) -> dict[str, T]:
    if opt is None:
        return {}
    return opt


def _parse_external(ext: Optional[Union[bool, spec.External]]) -> bool:
    if ext is None:
        return False
    if isinstance(ext, bool):
        return ext
    return str(ext).lower() == "true"


class EnvFileInfo:
    def __init__(
        self,
        path: str,
        required: Optional[bool] = True,
    ) -> None:
        self.path = path
        self.required = True if required is None else required


class Service:
    # pylint: disable=too-many-arguments,too-many-instance-attributes,too-many-positional-arguments,too-many-locals
    def __init__(
        self,
        source_file: str,
        name: str,
        annotations: dict[str, str],
        labels: dict[str, str],
        image: Optional[str] = None,
        ports: Optional[list[Port]] = None,
        networks: Optional[list[str]] = None,
        volumes: Optional[list[Volume]] = None,
        depends_on: Optional[dict[str, spec.DependsOn]] = None,
        links: Optional[list[str]] = None,
        extends: Optional[Extends] = None,
        cgroup_parent: Optional[str] = None,
        container_name: Optional[str] = None,
        devices: Optional[list[Device]] = None,
        env_file: Optional[dict[str, EnvFileInfo]] = None,
        expose: Optional[list[str]] = None,
        profiles: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.image = image
        self.ports = opt_to_arr(ports)
        self.networks = opt_to_arr(networks)
        self.volumes = opt_to_arr(volumes)
        self.depends_on = opt_to_dict(depends_on)
        self.links = opt_to_arr(links)
        self.extends = extends
        self.cgroup_parent = cgroup_parent
        self.container_name = container_name
        self.devices = opt_to_arr(devices)
        self.env_file = opt_to_dict(env_file)
        self.expose = opt_to_arr(expose)
        self.profiles = opt_to_arr(profiles)
        self.labels = labels
        self.annotations = annotations
        self.source_files: list[str] = [source_file]

    def merge(self, other: "Service") -> None:
        """
        Merge a service with a pre-existing definition.

        All attributes of other parameter will replace or merge existing ones when set.
        """
        if other.image:
            self.image = other.image
        if other.name:
            self.name = other.name


class Network:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, source_file: str, network: spec.Network) -> None:
        self.name: Optional[str] = None
        self.driver: Optional[str] = None
        self.driver_opts: Optional[dict[str, Union[str, float]]] = None
        self.ipam: Optional[spec.Ipam] = None
        self.external = _parse_external(network.external)
        self.internal: bool = False if network.internal is None else network.internal
        self.enable_ipv6: Optional[bool] = network.enable_ipv6
        self.attachable: Optional[bool] = network.attachable
        self.labels: dict[str, str] = parse_list_of_dict_of_tuples(network.labels)
        self.source_file = [source_file]


class Secret:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, source_file: str, secret: spec.Secret) -> None:
        self.name: Optional[str] = secret.name
        self.environment: Optional[str] = secret.environment
        self.file: Optional[str] = secret.file
        self.external = _parse_external(secret.external)
        self.labels = parse_list_of_dict_of_tuples(secret.labels)
        self.driver: Optional[str] = secret.driver
        self.driver_opts: dict[str, Union[str, float]] = (
            secret.driver_opts if secret.driver_opts else {}
        )
        self.template_driver: Optional[str] = secret.template_driver
        self.source_file = [source_file]


class Config:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, source_file: str, config: spec.Config) -> None:
        self.name: Optional[str] = config.name
        self.content: Optional[str] = config.content
        self.environment: Optional[str] = config.environment
        self.file: Optional[str] = config.file
        self.external = _parse_external(config.external)
        self.labels = parse_list_of_dict_of_tuples(config.labels)
        self.template_driver: Optional[str] = config.template_driver
        self.source_file = [source_file]


class RootVolume:
    def __init__(self, source_file, volume=spec.Volume) -> None:
        if volume is None:
            volume = spec.Volume()
        self.name: Optional[str] = volume.name
        self.driver = volume.driver
        self.driver_opts = parse_list_of_dict_of_tuples(volume.driver_opts)
        self.external = _parse_external(volume.external)
        self.labels = parse_list_of_dict_of_tuples(volume.labels)
        self.source_file = [source_file]
