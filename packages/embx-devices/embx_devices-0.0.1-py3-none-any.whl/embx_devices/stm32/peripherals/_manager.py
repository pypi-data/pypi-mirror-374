import copy

from ..device_name import DevName
from ..mask import create_mask
from ..cubemx import DevData, DevPeripheral
from ._utils import get_peripheral_from_db
from ._models import Peripheral, PeripheralDef, PeripheralMasked


_stm32_ignored_peripherals = [
    "fatfs",
    "freertos",
    "libjpeg",
    "mbedtls",
    "pdm2pcm",
    "usb_device",
    "usb_host",
    "usb_otg_fs",
    "usb_otg_hs",
    "wwdg",
    "nvic",
]


class PeripheralDataManager:
    def __init__(self, devices_data: list[DevData]):
        self._devices_data = devices_data

        self._peripherals_by_device: dict[str, list[Peripheral]] = dict()

    def get_all_peripherals(self) -> list[PeripheralMasked]:
        self.__do_initial_processing()

        merged_by_version = self.__merge_by_version()
        masked_peripherals = self.__create_masked_peripherals(merged_by_version)

        final_peripherals = self.__merge_by_devices(masked_peripherals)

        final_peripherals.sort(key=lambda s: (s.name, s.instances))
        return final_peripherals

    def __merge_by_devices(
        self,
        peripherals: list[PeripheralMasked],
    ) -> list[PeripheralMasked]:
        for i in range(len(peripherals) - 1, -1, -1):
            for j in range(i - 1, -1, -1):
                p_i, p_j = peripherals[i], peripherals[j]
                if self.__can_merge_by_devices(p_i, p_j):
                    peripherals[j] = PeripheralMasked(
                        name=p_j.name,
                        instances=p_j.instances + p_i.instances,
                        version=p_j.version,
                        tags=p_i.tags,
                        mask=p_i.mask,
                    )
                    peripherals.pop(i)
                    break

        return peripherals

    @staticmethod
    def __can_merge_by_devices(p1: PeripheralMasked, p2: PeripheralMasked) -> bool:
        return (
            p1.name == p2.name
            and p1.version == p2.version
            and p1.tags == p2.tags
            and p1.mask == p2.mask
        )

    @staticmethod
    def __create_masked_peripherals(
        merged_by_version: dict[Peripheral, set[str]],
    ) -> list[PeripheralMasked]:
        masked_peripherals: list[PeripheralMasked] = []
        for p in merged_by_version.keys():
            mask = create_mask(cubemx_devices=list(merged_by_version[p]))
            masked_peripherals.append(
                PeripheralMasked(
                    name=p.name,
                    instances=p.instances,
                    version=p.version,
                    tags=p.tags,
                    mask=mask,
                )
            )
        return masked_peripherals

    def __merge_by_version(self) -> dict[Peripheral, set[str]]:
        merged_by_version: dict[Peripheral, set[str]] = dict()
        for dev in self._peripherals_by_device.keys():
            for p in self._peripherals_by_device[dev]:
                if p not in merged_by_version.keys():
                    merged_by_version[p] = {dev}
                else:
                    merged_by_version[p].add(dev)
        return merged_by_version

    @staticmethod
    def __remove_ignored_peripherals(
        input_peripherals: list[DevPeripheral],
    ) -> list[DevPeripheral]:
        output_peripherals = []
        for p in input_peripherals:
            if p.name not in _stm32_ignored_peripherals:
                output_peripherals.append(p)
        return output_peripherals

    def __do_initial_processing(self):
        for dev_data in self._devices_data:
            peripherals = self.__remove_ignored_peripherals(dev_data.peripherals)
            peripherals_embx = self.__apply_embx_versions(
                peripherals, dev_data.devices[0]
            )
            self._peripherals_by_device[dev_data.cubemx_device] = peripherals_embx

    @staticmethod
    def __apply_embx_versions(
        cube_peripherals: list[DevPeripheral], dev: DevName
    ) -> list[Peripheral]:
        output = []
        for p in cube_peripherals:
            db_elem: PeripheralDef = get_peripheral_from_db(p.name, p.instance, dev)

            output.append(
                Peripheral(p.name.lower(), (p.instance,), db_elem.version, db_elem.tags)
            )
        return output
