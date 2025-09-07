import os
from pathlib import Path
import json
from dataclasses import asdict

from .device_group import DevGroup
from .cubemx import FamiliesFile, ValidDevices, DevData, MCUFile
from .device_data import STM32Data

from .memory import MemoryDataManager, MemMap
from .peripherals import PeripheralDataManager, PeripheralMasked


class DeviceDataGenerator:
    def __init__(self, cubemx_db_folder: str | Path, output_folder: str | Path):
        self._db_folder = os.path.abspath(cubemx_db_folder)
        self._mcu_folder = os.path.join(self._db_folder, "mcu")
        self._ip_folder = os.path.join(self._mcu_folder, "IP")
        self._output_folder = os.path.abspath(output_folder)

        self._valid_devices: ValidDevices | None = None
        self._memory_map: MemMap | None = None
        self._peripherals: list[PeripheralMasked] | None = None

        self._data: STM32Data | None = None

    def generate(self, dev_group: DevGroup):
        families_file = FamiliesFile(os.path.join(self._mcu_folder, "families.xml"))
        self._valid_devices = families_file.extract_valid_devices(dev_group)

        devices_data: list[DevData] = []
        for cubemx_name in self._valid_devices.cubemx_names:
            filepath = os.path.join(self._mcu_folder, f"{cubemx_name}.xml")
            mcu_file = MCUFile(filepath)
            devices_data.append(mcu_file.extract_all_data())

        memory_data_collector = MemoryDataManager(devices_data=devices_data)
        self._memory_map = memory_data_collector.get_memory_map()

        peripheral_data_collector = PeripheralDataManager(devices_data=devices_data)
        self._peripherals = peripheral_data_collector.get_all_peripherals()

        self.__compose_data()
        output_filepath = os.path.join(self._output_folder, f"{dev_group.name}.json")
        self.__save_data_as_json(output_filepath)

    def __compose_data(self):
        devices = [dev.model for dev in self._valid_devices.devices]

        self._data = STM32Data(
            devices=devices,
            memory=self._memory_map,
            peripherals=self._peripherals,
        )

    def __save_data_as_json(self, filepath: str):
        data_dict = asdict(self._data)
        data_json = json.dumps(data_dict, indent=4)
        with open(filepath, "w") as f:
            f.write(data_json)
