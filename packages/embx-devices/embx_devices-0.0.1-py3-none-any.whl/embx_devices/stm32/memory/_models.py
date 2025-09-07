from dataclasses import dataclass
from enum import StrEnum


class MemSegType(StrEnum):
    FLASH = "flash"
    CCM = "ccm"
    SRAM1 = "sram1"
    SRAM2 = "sram2"
    SRAM3 = "sram3"
    BACKUP = "backup"


@dataclass(slots=True, frozen=True)
class MemSeg:
    seg_type: MemSegType
    start: int
    size: int | None

    @classmethod
    def from_dict(cls, d: dict):
        return cls(MemSegType(d["seg_type"]), d["start"], d["size"])


@dataclass(slots=True, frozen=True)
class MemSegMasked:
    seg_type: MemSegType
    start: int
    size: int
    mask: str


@dataclass(slots=True, frozen=True)
class MemMap:
    segments: list[MemSegMasked]
