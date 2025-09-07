from typing import Sequence
from itertools import product
import re

from .device_name import DevName, expand_name_variants
from .._logger import logger

_mask_part_pattern = re.compile(
    r"\["
    r"(?P<family>.*?)"
    r"]\["
    r"(?P<lines>.*?)"
    r"]\["
    r"(?P<postfixes>.*?)"
    r"]"
)


class NoDevicesSpecifiedError(Exception):
    def __init__(self):
        super().__init__(
            f"Can't create mask: both 'devices' and 'cubemx_devices' are None"
        )


def create_mask(
    devices: Sequence[DevName] | None = None,
    cubemx_devices: Sequence[str] | None = None,
) -> str:
    if devices is None:
        if cubemx_devices is not None:
            devices = [
                DevName.from_str(n)
                for dev in cubemx_devices
                for n in expand_name_variants(dev)
            ]
        else:
            logger.error(
                f"Can't create mask: both 'devices' and 'cubemx_devices' are None"
            )
            raise NoDevicesSpecifiedError()

    families = set()
    lines = set()
    data = {}

    for name in devices:
        families.add(family := name.family)
        lines.add(line := name.line)
        postfix = f"{name.pin}{name.memory}{name.package}"
        if family not in data:
            data[family] = {}
        if line not in data[family]:
            data[family][line] = []
        data[family][line].append(postfix)

    for family in data.keys():
        for line in data[family].keys():
            data[family][line].sort()

    groups = []
    for family, line in product(sorted(families), sorted(lines)):
        # Check if family line combination exists
        if not (family in data and line in data[family]):
            continue
        merged = False
        for group in groups:
            if group[2] == data[family][line] and group[0] == family:
                group[1].append(line)
                merged = True
                break

        if not merged:
            groups.append([family, [line], data[family][line]])

    mask_parts = [
        f"[{group[0]}][{'|'.join(group[1])}][{'|'.join(group[2])}]" for group in groups
    ]
    return "|".join(mask_parts)


def check_mask(
    mask: str,
    device: DevName,
) -> bool:
    family = device.family
    line = device.line
    postfix = f"{device.pin}{device.memory}{device.package}"

    for match in _mask_part_pattern.finditer(mask):
        mask_families = match.group("family").split("|")
        mask_lines = match.group("lines").split("|")
        mask_postfixes = match.group("postfixes").split("|")

        if "*" in mask_families or family in mask_families:
            if "*" in mask_lines or line in mask_lines:
                if "*" in mask_postfixes or postfix in mask_postfixes:
                    return True
    return False
