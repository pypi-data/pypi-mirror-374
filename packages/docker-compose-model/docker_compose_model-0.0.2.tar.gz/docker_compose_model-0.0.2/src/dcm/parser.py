import re
from typing import Any, Callable, Optional, TypeVar, Union

from pydantic_yaml import parse_yaml_file_as

from . import spec
from .models import (
    Config,
    Device,
    EnvFileInfo,
    Extends,
    Network,
    Port,
    RootVolume,
    Secret,
    Service,
    Volume,
    VolumeType,
    parse_list_of_dict_of_tuples,
)


class Compose:
    def __init__(self) -> None:
        self.include: list[spec.Include] = []
        self.services: dict[str, Service] = {}
        self.configs: dict[str, Config] = {}
        self.networks: dict[str, Network] = {}
        self.secrets: dict[str, Secret] = {}
        self.volumes: dict[str, RootVolume] = {}


def parse_port(
    source_file: str, port_data: Union[float, str, spec.Ports]
) -> Optional[Port]:
    if isinstance(port_data, float):
        return Port(source_file, "0.0.0.0", str(int(port_data)), str(int(port_data)))
    if isinstance(port_data, str):
        regex = r"((?P<host_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:|(\$\{([^}]+)\}):)|:|)?((?P<host_port>\d+(\-\d+)?):)?((?P<container_port>\d+(\-\d+)?))?(/(?P<protocol>\w+))?"  # noqa: E501
        match = re.match(regex, port_data)

        if match:
            host_ip = match.group("host_ip")
            host_port = match.group("host_port")
            container_port = match.group("container_port")

            if container_port is not None and host_port is None:
                host_port = container_port

            if host_ip is not None:
                return Port(
                    source_file=source_file,
                    host=host_ip,
                    source_port=host_port,
                    container_port=container_port,
                )
            return Port(
                source_file=source_file,
                host="0.0.0.0",
                source_port=host_port,
                container_port=container_port,
            )
        return None
    if isinstance(port_data, spec.Ports):
        host_ip = port_data.host_ip if port_data.host_ip else "0.0.0.0"
        host_port = str(
            port_data.published if port_data.published else port_data.published
        )
        if not port_data.target:
            return None
        return Port(
            source_file=source_file,
            host=host_ip,
            source_port=host_port,
            container_port=str(port_data.target),
        )
    raise RuntimeError("LogicError while parsing port")


def _unwrap_depends_on(
    data_depends_on: Union[spec.ListOfStrings, dict[Any, spec.DependsOn], None],
) -> dict[str, spec.DependsOn]:
    if isinstance(data_depends_on, spec.ListOfStrings):
        return {
            k: spec.DependsOn(
                restart=True, required=True, condition=spec.Condition.service_started
            )
            for k in data_depends_on.root
        }
    if isinstance(data_depends_on, dict):
        return data_depends_on
    return {}


TypeAspec = TypeVar("TypeAspec")
TypeAPrime = TypeVar("TypeAPrime")


class Parser:
    def __init__(self) -> None:
        pass

    def _parse_service(
        self, source_file: str, service_name: str, service_data: spec.Service
    ) -> Service:
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        service_image: Optional[str] = None
        if service_data.build is not None:
            if isinstance(service_data.build, str):
                service_image = f"build from '{service_data.build}'"
            elif isinstance(service_data.build, spec.Build):
                if (
                    service_data.build.context is not None
                    and service_data.build.dockerfile is not None
                ):
                    service_image = f"build from '{service_data.build.context}' using '{service_data.build.dockerfile}'"
                elif service_data.build.context is not None:
                    service_image = f"build from '{service_data.build.context}'"
        if service_data.image is not None:
            if service_image is not None:
                service_image += ", image: " + service_data.image
            else:
                service_image = service_data.image

        service_networks: list[str] = []
        if service_data.networks is not None:
            if isinstance(service_data.networks, spec.ListOfStrings):
                service_networks = service_data.networks.root
            elif isinstance(service_data.networks, dict):
                service_networks = list(service_data.networks.keys())

        service_extends: Optional[Extends] = None
        if service_data.extends is not None:
            # https://github.com/compose-spec/compose-spec/blob/master/spec.md#extends
            # The value of the extends key MUST be a dictionary.
            assert isinstance(service_data.extends, spec.Extends)
            service_extends = Extends(
                service_name=service_data.extends.service,
                from_file=service_data.extends.file,
            )

        service_ports: list[Port] = []
        if service_data.ports is not None:
            for port_data in service_data.ports:
                port = parse_port(source_file=source_file, port_data=port_data)
                if port:
                    service_ports.append(port)

        service_depends_on = _unwrap_depends_on(service_data.depends_on)

        service_volumes: list[Volume] = []
        if service_data.volumes is not None:
            for volume_data in service_data.volumes:
                if isinstance(volume_data, str):
                    assert ":" in volume_data, "Invalid volume input, aborting."

                    split_data = volume_data.split(":")
                    source = split_data[0]
                    if len(split_data) == 2:
                        service_volumes.append(
                            Volume(
                                source_file=source_file,
                                source=source,
                                target=split_data[1],
                            )
                        )
                    elif len(split_data) == 3:
                        service_volumes.append(
                            Volume(
                                source_file=source_file,
                                source=source,
                                target=split_data[1],
                                access_mode=split_data[2],
                            )
                        )
                elif isinstance(volume_data, spec.Volumes):
                    assert volume_data.target is not None, (
                        "Invalid volume input, aborting."
                    )

                    # https://github.com/compose-spec/compose-spec/blob/master/spec.md#long-syntax-4
                    # `volume_data.source` is not applicable for a tmpfs mount.
                    if volume_data.source is None:
                        volume_data.source = volume_data.target

                    assert volume_data.source is not None
                    source = volume_data.source

                    service_volumes.append(
                        Volume(
                            source_file=source_file,
                            source=source,
                            target=volume_data.target,
                            v_type=VolumeType[volume_data.type],
                        )
                    )

        service_links: list[str] = []
        if service_data.links is not None:
            service_links = service_data.links

        cgroup_parent: Optional[str] = None
        if service_data.cgroup_parent is not None:
            cgroup_parent = service_data.cgroup_parent

        container_name: Optional[str] = None
        if service_data.container_name is not None:
            container_name = service_data.container_name

        env_file: dict[str, EnvFileInfo] = {}
        if service_data.env_file is not None:
            if isinstance(service_data.env_file.root, str):
                env_file[service_data.env_file.root] = EnvFileInfo(
                    service_data.env_file.root
                )
            elif isinstance(service_data.env_file.root, list):
                for env_file_data in service_data.env_file.root:
                    if isinstance(env_file_data, str):
                        env_file[env_file_data] = EnvFileInfo(env_file_data)
                    elif isinstance(env_file_data, spec.EnvFile1):
                        env_file[env_file_data.path] = EnvFileInfo(
                            path=env_file_data.path, required=env_file_data.required
                        )
            else:
                print(f"Invalid env_file data: {service_data.env_file.root}")

        expose: list[str] = []
        if service_data.expose is not None:
            for ex_port in service_data.expose:
                # to avoid to have values like 8885.0 for instance, cast floats into int first
                port_str = (
                    str(int(ex_port)) if isinstance(ex_port, float) else str(ex_port)
                )
                expose.append(port_str)

        profiles: list[str] = []
        if service_data.profiles is not None:
            if isinstance(service_data.profiles, spec.ListOfStrings):
                profiles = service_data.profiles.root

        devices: list[Device] = []
        if service_data.devices is not None:
            for device_data in service_data.devices:
                if isinstance(device_data, str):
                    assert ":" in device_data, "Invalid volume input, aborting."

                    split_data = device_data.split(":")
                    if len(split_data) == 2:
                        devices.append(
                            Device(
                                source_file=source_file,
                                host_path=split_data[0],
                                container_path=split_data[1],
                            )
                        )
                    elif len(split_data) == 3:
                        devices.append(
                            Device(
                                source_file=source_file,
                                host_path=split_data[0],
                                container_path=split_data[1],
                                cgroup_permissions=split_data[2],
                            )
                        )

        return Service(
            source_file=source_file,
            name=service_name,
            annotations=parse_list_of_dict_of_tuples(service_data.annotations),
            labels=parse_list_of_dict_of_tuples(service_data.labels),
            image=service_image,
            networks=service_networks,
            extends=service_extends,
            ports=service_ports,
            depends_on=service_depends_on,
            volumes=service_volumes,
            links=service_links,
            cgroup_parent=cgroup_parent,
            container_name=container_name,
            env_file=env_file,
            expose=expose,
            profiles=profiles,
            devices=devices,
        )

    def merge(
        self, main_compose: Compose, file: str, compose: spec.ComposeSpecification
    ) -> None:
        if compose.services:
            for service_name, service_data in compose.services.items():
                service = self._parse_service(
                    source_file=file,
                    service_name=service_name,
                    service_data=service_data,
                )
                if service_name in main_compose.services:
                    main_compose.services[service_name].merge(service)
                else:
                    main_compose.services[service_name] = service

        def merge(
            into: dict[str, TypeAPrime],
            val: Optional[dict[str, Any]],
            constructor: Callable[[str, TypeAspec], TypeAPrime],
        ) -> None:
            assert into is not None
            if val is None:
                return
            for k, v in val.items():
                if k not in into:
                    into[k] = constructor(file, v)

        if compose.include:
            main_compose.include.extend(compose.include)
        merge(main_compose.configs, compose.configs, Config)
        merge(main_compose.networks, compose.networks, Network)
        merge(main_compose.secrets, compose.secrets, Secret)
        merge(main_compose.volumes, compose.volumes, RootVolume)


def parse_compose_files(*file_list: str) -> Compose:
    compose_result = Compose()
    parser = Parser()
    for f in file_list:
        res = parse_yaml_file_as(spec.ComposeSpecification, f)
        parser.merge(main_compose=compose_result, file=f, compose=res)
    return compose_result
