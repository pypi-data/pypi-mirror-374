from dataclasses import dataclass

from ..device_name import DevName


@dataclass(slots=True, frozen=True)
class ValidDevices:
    cubemx_names: list[str]
    devices: list[DevName]


@dataclass(slots=True, frozen=True)
class DevMemory:
    flash_size: int
    ram_size: int
    ccm_size: int | None


@dataclass(slots=True, frozen=True)
class DevPeripheral:
    name: str
    instance: int
    cubemx_version: str


@dataclass(slots=True, frozen=True)
class DevData:
    cubemx_device: str
    devices: list[DevName]
    memory_variants: list[DevMemory]
    peripherals: list[DevPeripheral]
