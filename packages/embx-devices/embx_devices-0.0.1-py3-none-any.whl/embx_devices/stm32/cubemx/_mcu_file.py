import copy
from xml.etree.ElementTree import Element

from ...utils.base_xml_parser import BaseXMLParser
from ..device_name import DevName, expand_name_variants
from ._models import DevData, DevMemory, DevPeripheral
from ..peripherals import PeripheralName


class MCUFile(BaseXMLParser):
    def __init__(self, filepath: str):
        super().__init__(filepath=filepath)

        self.register_namespace(self._root, "mcu")

        self._cubemx_device = self._root.get("RefName")
        self._devices = [
            DevName.from_str(dev) for dev in expand_name_variants(self._cubemx_device)
        ]

    def __extract_memory(self) -> list[DevMemory]:
        flash_elems = self._root.findall("mcu:Flash", self._ns)
        flash_variants = [int(elem.text) * 1024 for elem in flash_elems]

        ram_elems = self._root.findall("mcu:Ram", self._ns)
        ram_variants = [int(elem.text) * 1024 for elem in ram_elems]

        ccm_elem = self._root.find("mcu:CCMRam", self._ns)
        ccm = int(ccm_elem.text) * 1024 if ccm_elem is not None else None

        output: list[DevMemory] = []
        for dev, dev_flash, dev_ram in zip(self._devices, flash_variants, ram_variants):
            output.append(DevMemory(dev_flash, dev_ram, ccm))
        return output

    def __extract_peripherals(self):
        peripherals: list[DevPeripheral] = []
        for peripheral_elem in self._root.findall("mcu:IP", self._ns):
            instance_str = peripheral_elem.get("InstanceName")
            version = peripheral_elem.get("Version")

            parsed_name = PeripheralName.from_str(instance_str)
            peripherals.append(
                DevPeripheral(
                    name=parsed_name.name,
                    instance=parsed_name.instance,
                    cubemx_version=version,
                )
            )
        return peripherals

    def extract_all_data(self) -> DevData:
        memory = self.__extract_memory()
        peripherals = self.__extract_peripherals()

        return DevData(
            cubemx_device=self._cubemx_device,
            devices=self._devices,
            memory_variants=memory,
            peripherals=peripherals,
        )
