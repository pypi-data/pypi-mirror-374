import copy

from ._utils import get_segments_from_db
from ._models import MemSegType, MemSegMasked, MemSeg, MemMap
from ..device_name import DevName
from ..mask import create_mask
from ..cubemx import DevData


class MemoryDataManager:
    def __init__(self, devices_data: list[DevData]):
        self._devices_data = devices_data

    def __get_devices_by_segment(self) -> dict[MemSeg, list[DevName]]:
        devices_by_segment = dict()

        for dev_data in self._devices_data:
            for dev_memory, dev in zip(dev_data.memory_variants, dev_data.devices):
                dev_segments = get_segments_from_db(dev)
                for dev_seg in dev_segments:
                    if dev_seg.seg_type == MemSegType.FLASH:
                        segment = MemSeg(
                            MemSegType.FLASH, dev_seg.start, dev_memory.flash_size
                        )
                    else:
                        segment = copy.deepcopy(dev_seg)

                    if segment in devices_by_segment.keys():
                        devices_by_segment[segment].add(dev)
                    else:
                        devices_by_segment[segment] = {dev}
        return devices_by_segment

    def get_memory_map(self) -> MemMap:
        devices_by_segment = self.__get_devices_by_segment()
        masked_segments: list[MemSegMasked] = []

        for segment in devices_by_segment.keys():
            mask = create_mask(devices=devices_by_segment[segment])
            masked_segments.append(
                MemSegMasked(segment.seg_type, segment.start, segment.size, mask)
            )

        masked_segments.sort(key=lambda s: (s.seg_type.value, s.size))

        return MemMap(segments=masked_segments)
