from ._db import stm32_memory_db
from ..device_name import DevName
from ._models import MemSeg
from ..mask import check_mask


def get_segments_from_db(dev: DevName) -> list[MemSeg]:
    found_segments: list[MemSeg] = []

    for mask in stm32_memory_db.keys():
        if check_mask(mask, dev):
            found_segments += stm32_memory_db[mask]

    return found_segments
