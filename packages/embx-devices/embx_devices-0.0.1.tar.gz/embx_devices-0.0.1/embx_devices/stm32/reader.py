import os
from pathlib import Path
import json

from .device_name import DevName
from .mask import check_mask
from .._logger import logger

from .memory import MemSeg
from .peripherals import Peripheral


class FileNotFoundForDevice(Exception):
    def __init__(self, device: str):
        super().__init__(f"No file with data for '{device}' device")


class DeviceDataReader:
    def __init__(self, folder: str | Path):
        self._data_folder = folder
        self._device: DevName | None = None

        self._data: dict | None = None

    def set_device(self, dev_name: str):
        self._device = DevName.from_str(dev_name)
        self.__find_data_file()

    def __find_data_file(self):
        try:
            filenames = [
                f for f in os.listdir(self._data_folder) if f.find(".json") > 0
            ]
            for filename in filenames:
                filepath = os.path.join(self._data_folder, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                if self._device.model in data["devices"]:
                    self._data = data
                    return
            raise FileNotFoundForDevice(self._device.model)

        except FileNotFoundForDevice:
            logger.exception("Can't find device data file for provided device")
            raise

    def get_memory_segments(self) -> list[MemSeg]:
        return [
            MemSeg.from_dict(seg_data)
            for seg_data in self._data["memory"]["segments"]
            if check_mask(seg_data["mask"], self._device)
        ]

    def get_peripheral(self, name: str, instance: int) -> Peripheral | None:
        for periph_data in self._data["peripherals"]:
            if name == periph_data["name"] and instance in periph_data["instances"]:
                if check_mask(periph_data["mask"], self._device):
                    return Peripheral.from_dict(periph_data)
        return None
