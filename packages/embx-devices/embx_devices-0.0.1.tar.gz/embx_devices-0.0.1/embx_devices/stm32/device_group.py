from dataclasses import dataclass
from typing import Sequence

from .device_name import DevName


@dataclass
class DevSubgroup:
    line: str
    pin: Sequence[str]
    memory: Sequence[str]


@dataclass
class DevGroup:
    name: str
    family: str
    subgroups: list[DevSubgroup]

    def includes_device(self, device: DevName) -> bool:
        if device.family != self.family:
            return False

        for subgroup in self.subgroups:
            if (
                device.line == subgroup.line
                and device.pin in subgroup.pin
                and device.memory in subgroup.memory
            ):
                return True
        return False
